# Lain Wired

+ Author: Flan
+ Category: web
+ Intended difficulty: easy
+ Solves during competition: 7/10

## The challenge
Users are given a single app where they can register, log in and need to activate their account using a 4-digit OTP. The OTP check is exposed thrgouh GraphQL and is rate-limited per request. Once activated, the users can submit CSS for an admin to review. The admin review page loads the user submitted CSS and contains hidder per-submission release metadata in DOM attributes.

The goal is to activate an account, leak the hidden review metadata from the
admin bot, and use it to publish the submission.

## Solution
Users must first create an account and log in. They will be asked for a OTP that they don't have, but the rate-limiting only limits the number of HTTP requests, not the number of GraphQL resolver calls inside a single request. Use GraphQL aliases to try all 10000 OTP values and activate the account. 

Once verified, submit malicious CSS. The admin bot visits
`/internal/preview/:id`, which loads `/submission/:id.css` and places the
submission's `publish_key` and `review_revision` one character at a time into
`data-proof` and `data-phase` attributes. CSS attribute selectors can test each
hex character and trigger a request to `/r` when a guess matches.

The `/r` requests are stored in telemetry and can be read back from
`/telemetry`. Reconstruct the leaked `publish_key` and `review_revision`, then
submit them with the submission id to `/internal/publish` to receive the flag.
