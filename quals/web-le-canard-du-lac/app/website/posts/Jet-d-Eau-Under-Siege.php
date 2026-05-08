<?php

$post_title = "Jet d'Eau Under Siege: A Deep Dive into Geneva's Water System";
$post_brief = "Is the iconic Jet d'Eau more than just a tourist attraction? We investigate the latent vulnerabilities in the city's water management system. A tale of intrigue, civic infrastructure, and questionable SCADA security.";

$post_content = <<<HTML
    <img class="img-fluid w-100 mb-4" src="static/images/jet_d_eau_hacked.png" alt="Hacked Jet d'Eau">

    <p class="card-text">
        To tourists, Geneva's Jet d'Eau is a majestic plume of water against the sky. To us, it's a 140-meter-high, publicly accessible attack surface. We decided to take a deep dive into the SCADA systems that control Geneva's water pressure, and what we found was... leaky.
    </p>

    <h2 class="card-title mt-4">SCADA? More Like SCAD-uh-oh!</h2>
    <p class="card-text">
        The industrial control systems (ICS) that manage civic infrastructure are notoriously insecure. We're talking about systems designed in the 90s, now connected to the internet for "convenience." Our investigation suggests the Jet d'Eau's control panel is accessible via a web interface with default credentials that are probably `admin:password123`.
    </p>
    <p class="card-text">
        Imagine the possibilities. A skilled attacker could weaponize the fountain, aiming its powerful jet at nearby buildings. Or, for the more artistically inclined hacker, they could modulate the water pressure to send messages in Morse code. We suspect a rival faction of hackers has already tried it, but their message was garbled. They probably forgot to URL-encode their payload. Amateurs.
    </p>

    <h2 class="card-title mt-4">Stuxnet for Fountains</h2>
    <p class="card-text">
        This isn't just about a fountain; it's about the vulnerability of our critical infrastructure. If the Jet d'Eau is this exposed, what about the rest of the city's systems? For now, the fountain remains a symbol of Geneva. But it's also a reminder that with enough skill, you can pwn just about anything. Even water. 💧
    </p>
HTML;
