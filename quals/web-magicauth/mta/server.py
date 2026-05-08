import asyncio
import logging
from email import message_from_bytes

from aiosmtpd.controller import Controller

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 25
FORWARD_HOST = "smtp2http"
FORWARD_PORT = 25

class MTAHandler:
    async def handle_DATA(self, server, session, envelope):
        try:
            peer = session.peer
            client_ip = peer[0] if peer else "unknown"

            logger.info(f"Received email from {client_ip}: {envelope.mail_from} -> {envelope.rcpt_tos}")

            message_data = envelope.content

            msg = message_from_bytes(message_data)

            # Security: Remove any existing Received headers to prevent spoofing
            # Only the last MTA's Received header should be trusted
            if 'Received' in msg:
                del msg['Received']

            msg['Received'] = client_ip

            await self.forward_email(
                msg,
                envelope.mail_from,
                envelope.rcpt_tos
            )

            return '250 OK: Message accepted for delivery'

        except Exception as e:
            logger.error(f"Error processing email: {e}", exc_info=True)
            return '451 Requested action aborted: error in processing'

    async def forward_email(self, msg, mail_from, rcpt_tos):
        try:
            reader, writer = await asyncio.open_connection(FORWARD_HOST, FORWARD_PORT)

            # Read banner
            banner = await reader.readline()
            logger.debug(f"smtp2http banner: {banner.decode().strip()}")

            # Send EHLO
            writer.write(b"EHLO mta\r\n")
            await writer.drain()
            response = await reader.readline()
            logger.debug(f"EHLO response: {response.decode().strip()}")

            # Send MAIL FROM
            writer.write(f"MAIL FROM:<{mail_from}>\r\n".encode())
            await writer.drain()
            response = await reader.readline()
            logger.debug(f"MAIL FROM response: {response.decode().strip()}")

            # Send RCPT TO for each recipient
            for recipient in rcpt_tos:
                writer.write(f"RCPT TO:<{recipient}>\r\n".encode())
                await writer.drain()
                response = await reader.readline()
                logger.debug(f"RCPT TO response: {response.decode().strip()}")

            # Send DATA command
            writer.write(b"DATA\r\n")
            await writer.drain()
            response = await reader.readline()
            logger.debug(f"DATA response: {response.decode().strip()}")

            email_content = msg.as_string().encode('utf-8')
            writer.write(email_content)

            if not email_content.endswith(b"\r\n"):
                writer.write(b"\r\n")
            writer.write(b".\r\n")
            await writer.drain()
            response = await reader.readline()
            logger.debug(f"Message response: {response.decode().strip()}")

            # Send QUIT
            writer.write(b"QUIT\r\n")
            await writer.drain()
            response = await reader.readline()
            logger.debug(f"QUIT response: {response.decode().strip()}")

            writer.close()
            await writer.wait_closed()

            logger.info(f"Successfully forwarded email from {mail_from} to {rcpt_tos}")

        except Exception as e:
            logger.error(f"Failed to forward email: {e}", exc_info=True)

async def main():
    handler = MTAHandler()

    controller = Controller(
        handler,
        hostname=LISTEN_HOST,
        port=LISTEN_PORT
    )

    controller.start()
    logger.info(f"MTA listening on {LISTEN_HOST}:{LISTEN_PORT}")

    try:
        await asyncio.Event().wait()
    finally:
        controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
