<?php
// Enable loading of external entities
libxml_disable_entity_loader(false);

$feed_output = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $xml_content = $_POST['rss_content'];
    
    $dom = new DOMDocument();
    // LIBXML_NOENT is what enables entity substitution
    // LIBXML_DTDLOAD allows loading external DTDs
    if (@$dom->loadXML($xml_content, LIBXML_NOENT | LIBXML_DTDLOAD)) {
        $title_node = $dom->getElementsByTagName('title')->item(0);
        $desc_node = $dom->getElementsByTagName('description')->item(0);
        
        $feed_title = $title_node ? $title_node->nodeValue : "No Title";
        $feed_desc = $desc_node ? $desc_node->nodeValue : "No Description";
        
        $feed_output = "<div class='alert alert-success mt-3'>
            <h4 class='alert-heading'>Feed Validated!</h4>
            <p>Your feed looks great. Here is what we parsed:</p>
            <hr>
            <p><strong>title:</strong> " . htmlspecialchars($feed_title) . "</p>
            <p><strong>description:</strong> " . htmlspecialchars($feed_desc) . "</p>
        </div>";
    } else {
        $feed_output = "<div class='alert alert-danger mt-3'>Invalid XML content. Please check your syntax.</div>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | RSS Validator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Roboto+Mono:wght@400;700&display=swap"
        rel="stylesheet">
    <link href="static/lake-theme.css" rel="stylesheet">
    <link href="static/custom.css" rel="stylesheet">
</head>

<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Partner RSS Validator</h1>
                <p class="lead mb-0">Submit your RSS feed to join our syndicate!</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card my-4">
                    <div class="card-body">
                        <p>We are looking for local news partners. Validate your RSS feed here to see if it meets our technical standards.</p>
                        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                            <div class="form-group mb-3">
                                <label for="rss_content" class="form-label">RSS XML Content</label>
                                <textarea name="rss_content" id="rss_content" class="form-control" rows="10" placeholder="&lt;?xml version='1.0' encoding='UTF-8'?&gt;..."></textarea>
                            </div>
                            <div class="form-group">
                                <input type="submit" class="btn btn-primary" value="Validate Feed">
                            </div>
                        </form>
                        
                        <?php echo $feed_output; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>

</html>
