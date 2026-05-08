<?php
$author_alias = "";
$post_title = "";
$errors = [];
$success_message = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $author_alias = trim($_POST["author_alias"] ?? '');
    $post_title = trim($_POST["post_title"] ?? '');

    if (empty($author_alias)) {
        $errors['author_alias'] = "An author alias is required.";
    }

    if (empty($post_title)) {
        $errors['post_title'] = "A post title is required.";
    }

    if (isset($_FILES["articleFile"]) && $_FILES["articleFile"]["error"] == 0) {
        $allowed_extensions = ['php'];
        $allowed_mime_types = ['text/x-php', 'application/x-httpd-php'];

        $file_name = $_FILES["articleFile"]["name"];
        $file_tmp_name = $_FILES["articleFile"]["tmp_name"];
        $file_size = $_FILES["articleFile"]["size"];
        $file_mime_type = mime_content_type($file_tmp_name);
        $file_extension = strtolower(pathinfo($file_name, PATHINFO_EXTENSION));

        if ($file_size > 2000000) { // Limit file size to 2MB
            $errors['file'] = "Error: File is larger than the 2MB limit.";
        } elseif (!in_array($file_extension, $allowed_extensions)) {
            $errors['file'] = "Invalid file type. Only '.php' article templates are allowed.";
        } elseif (!in_array($file_mime_type, $allowed_mime_types)) {
            $errors['file'] = "Invalid MIME type. The server detected the file is not a PHP script.";
        } else {
            $target_dir = "/var/www/html/posts/";
            $safe_filename = preg_replace('/[^a-zA-Z0-9-]/', '', str_replace(' ', '-', $post_title)) . '.php';
            $target_file = $target_dir . $safe_filename;

            if (file_exists($target_file)) {
                $errors['file'] = "A post with this title already exists. Please choose a new title.";
            } else {
                if (!move_uploaded_file($file_tmp_name, $target_file)) {
                    $errors['file'] = "There was a critical error uploading the file.";
                }
            }
        }
    } else {
        $errors['file'] = "An article file is required for submission.";
    }

    if (empty($errors)) {
        $success_message = "Dispatch published successfully! The new article is now live.";
        $author_alias = "";
        $post_title = "";
    }
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | Admin Upload</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <link href="/static/lake-theme.css" rel="stylesheet">
    <link href="/static/custom.css" rel="stylesheet">
</head>

<body>
    <?php include("../include/navigation-bar.php"); ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Publish a Dispatch</h1>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card my-4">
                    <h5 class="card-header">New Article Submission</h5>
                    <div class="card-body">
                        <?php if (!empty($success_message)): ?>
                            <div class="alert alert-success" role="alert">
                                <?php echo $success_message; ?>
                            </div>
                        <?php endif; ?>

                        <p>Fill out the form to publish a new article to the front page. Only properly formatted `.php`
                            post templates are accepted.</p>

                        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post"
                            enctype="multipart/form-data" class="mt-4" novalidate>

                            <div class="mb-3">
                                <label for="post_title" class="form-label">Post Title</label>
                                <input type="text" name="post_title" id="post_title"
                                    class="form-control <?php echo isset($errors['post_title']) ? 'is-invalid' : ''; ?>"
                                    value="<?php echo htmlspecialchars($post_title); ?>" required>
                                <?php if (isset($errors['post_title'])): ?>
                                    <div class="invalid-feedback"><?php echo $errors['post_title']; ?></div>
                                <?php endif; ?>
                            </div>

                            <div class="mb-3">
                                <label for="author_alias" class="form-label">Author Alias</label>
                                <input type="text" name="author_alias" id="author_alias"
                                    class="form-control <?php echo isset($errors['author_alias']) ? 'is-invalid' : ''; ?>"
                                    value="<?php echo htmlspecialchars($author_alias); ?>" required>
                                <?php if (isset($errors['author_alias'])): ?>
                                    <div class="invalid-feedback"><?php echo $errors['author_alias']; ?></div>
                                <?php endif; ?>
                            </div>

                            <div class="mb-3">
                                <label for="articleFile" class="form-label">Article File (.php template)</label>
                                <input type="file" name="articleFile" id="articleFile"
                                    class="form-control <?php echo isset($errors['file']) ? 'is-invalid' : ''; ?>"
                                    required>
                                <?php if (isset($errors['file'])): ?>
                                    <div class="invalid-feedback"><?php echo $errors['file']; ?></div>
                                <?php endif; ?>
                            </div>

                            <div class="mt-4">
                                <button type="submit" class="btn btn-primary">Publish Article</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            <?php include("../include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>