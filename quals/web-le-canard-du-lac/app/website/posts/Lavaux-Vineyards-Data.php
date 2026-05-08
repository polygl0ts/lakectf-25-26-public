<?php

$post_title = "The Lavaux Vineyards: Are They Irrigated with Data?";
$post_brief = "The picturesque vineyards of Lavaux are a UNESCO World Heritage site. But what if the grapes are not just fed by water, but by data? We investigate the high-tech sensors and automated systems that run this ancient landscape.";

$post_content = <<<HTML
    <img class="img-fluid w-100 mb-4" src="static/images/lavaux_data.png" alt="Data Vineyards of Lavaux">

    <p class="card-text">
        The terraced vineyards of Lavaux are a testament to centuries of tradition. But beneath the idyllic surface lies a network of IoT devices, managing everything from soil acidity to sunlight exposure. The wine isn't just grown; it's compiled. And like any piece of software, it's vulnerable.
    </p>

    <h2 class="card-title mt-4">The Internet of Vines</h2>
    <p class="card-text">
        Drones patrol the skies, sensors dot the landscape, and automated irrigation systems deliver precise amounts of water. It's a marvel of agri-tech. But our probing revealed that the entire system is running on a dusty old version of PHP with known vulnerabilities. A simple SQL injection could alter the irrigation schedules.
    </p>
    <p class="card-text">
        Imagine a hacker running a query like: <code>UPDATE irrigation_schedule SET water_litres = 0 WHERE grape_type = 'Chasselas';</code> They could ruin an entire harvest without ever setting foot in the vineyard. Or worse, they could subtly alter the data to create a wine with a truly... unexpected flavor profile. A digital poison, if you will.
    </p>

    <h2 class="card-title mt-4">Root Access to the Root Stock</h2>
    <p class="card-text">
        This fusion of ancient tradition and modern tech creates unique security challenges. The winemakers of Lavaux need to worry not just about pests and weather, but also about patch management and SQL injection. Next time you enjoy a glass of local wine, ponder the data that went into making it. And hope the vineyard's firewall is stronger than their fermentation tanks. 🍇
    </p>
HTML;
