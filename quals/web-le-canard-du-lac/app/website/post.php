<?php
$file_to_include = "";
if (isset($_GET['id'])) {
    $file_to_include = "posts/" . basename($_GET['id']) . ".php";
    if (file_exists($file_to_include)) {
        include($file_to_include);
    }
}

if (!isset($post_title)) {
    if (!file_exists($file_to_include)) {
        $post_content = "<p>Post not found.</p>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | <?= isset($post_title) ? htmlspecialchars($post_title) : "Post"; ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link href="static/lake-theme.css" rel="stylesheet">
</head>

<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">
                    <?= isset($post_title) ? htmlspecialchars($post_title) : "Welcome"; ?>
                </h1>
                <p class="lead mb-3">
                    <?= isset($post_brief) ? htmlspecialchars($post_brief) : "--"; ?>
                </p>
            </div>
            <div class="text-center mt-4">
                <a href="index.php" class="btn btn-primary btn-lg">Back to Home</a>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card my-4">
                    <div class="card-body post-content">
                        <?= $post_content ?? ''; ?>
                    </div>
                </div>
            </div>

            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>

</html>