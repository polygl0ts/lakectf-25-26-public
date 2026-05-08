<?php
// Get the search query
$query = isset($_GET['query']) ? trim($_GET['query']) : '';

// Read the JSON file
$json_data = file_get_contents('posts.json');
$posts = json_decode($json_data, true);

$search_results = [];

if (!empty($query)) {
    // Filter posts based on the query
    foreach ($posts as $post) {
        if (stripos($post['title'], $query) !== false || stripos($post['content'], $query) !== false) {
            $search_results[] = $post;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | Search Results</title>
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
                <h1 class="fw-bolder">Search Results</h1>
                <?php if (!empty($query)): ?>
                    <p class="lead mb-0">Showing results for: "<?= htmlspecialchars($query); ?>"</p>
                <?php endif; ?>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if (!empty($search_results)): ?>
                    <?php foreach ($search_results as $post): ?>
                        <div class="card mb-4">
                            <img class="card-img-top img-fluid" src="<?= htmlspecialchars($post['image_url']); ?>"
                                style="max-height: 300px; object-fit: cover;" alt="<?= htmlspecialchars($post['title']); ?>">
                            <div class="card-body">
                                <h2 class="card-title"><?= htmlspecialchars($post['title']); ?></h2>
                                <p class="card-text"><?= htmlspecialchars($post['content']); ?></p>
                                <a href="post.php?id=<?= htmlspecialchars($post['post_url']); ?>" class="btn btn-primary">Read
                                    More →</a>
                            </div>
                        </div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <div class="card my-4">
                        <div class="card-body">
                            <p class="card-text">
                                <?php if (!empty($query)): ?>
                                    No articles found matching your search term. Try another keyword.
                                <?php else: ?>
                                    Please enter a search term in the sidebar to find articles.
                                <?php endif; ?>
                            </p>
                        </div>
                    </div>
                <?php endif; ?>
            </div>

            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>

</html>