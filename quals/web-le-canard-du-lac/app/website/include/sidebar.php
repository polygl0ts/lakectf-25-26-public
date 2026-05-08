<div class="col-md-4">
    <div class="card my-4">
        <h5 class="card-header">Search</h5>
        <div class="card-body">
            <form action="/search.php" method="GET">
                <div class="input-group">
                    <input type="text" name="query" class="form-control" placeholder="Search for..." required>
                    <button class="btn btn-primary" type="submit">Go!</button>
                </div>
            </form>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header">Hot Topics</h5>
        <div class="card-body">
            <div class="row">
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="/search.php?query=Warfare">Cyber-Warfare</a></li>
                        <li><a href="/search.php?query=Breach">Data Breaches</a></li>
                        <li><a href="/search.php?query=Surveillance">Surveillance</a></li>
                    </ul>
                </div>
                <div class="col-lg-6">
                    <ul class="list-unstyled mb-0">
                        <li><a href="/search.php?query=Conspiracy">Conspiracies</a></li>
                        <li><a href="/search.php?query=Crypto">Crypto Scams</a></li>
                        <li><a href="/search.php?query=Zero-Day">Zero-Days</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header">Active Surveillance</h5>
        <div class="card-body">
            <h6>Agents Online: <span id="visitorCount">0</span></h6>
            <p>Top Agencies:</p>
            <ul id="visitorCountries">
            </ul>
        </div>
    </div>

    <div class="card my-4">
        <h5 class="card-header">Become a Whistleblower</h5>
        <div class="card-body">
            <h6>Help us uncover the truth.</h6>
            <p>Submit your leaks <a href="/contact.php">here!</a></p>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        const countries = ["Argentina", "Poland", "USA", "Canada", "Brazil", "India", "Germany", "France",
            "Australia", "Japan", "South Korea", "South Africa"
        ];

        function updateVisitors() {
            const visitorCount = Math.floor(Math.random() * 500) + 100;
            document.getElementById('visitorCount').innerText = visitorCount;
            const selectedCountries = [];
            for (let i = 0; i < 3; i++) {
                const index = Math.floor(Math.random() * countries.length);
                if (!selectedCountries.includes(countries[index])) {
                    selectedCountries.push(countries[index]);
                }
            }
            const ul = document.getElementById('visitorCountries');
            ul.innerHTML = "";
            selectedCountries.forEach(country => {
                const li = document.createElement('li');
                li.innerText = country;
                ul.appendChild(li);
            });
        }
        updateVisitors();
        setInterval(updateVisitors, 5000);
    });
</script>