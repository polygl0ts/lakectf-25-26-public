<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | Contact</title>
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
                <h1 class="fw-bolder">Submit a Tip!</h1>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card my-4">
                    <div class="card-body">
                        <?php if (empty($succ_message)) { ?>
                        <p>Please fill in this form to send us a message.</p>
                        <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                            <div class="form-group mb-3">
                                <label>Alias (Optional)</label>
                                <input type="text" name="name" class="form-control" value="<?php echo $name; ?>">
                                <span class="error"><?php echo $name_err; ?></span>
                            </div>
                            <div class="form-group mb-3">
                                <label>Secure Drop (Optional)</label>
                                <input type="email" name="email" class="form-control" value="<?php echo $email; ?>">
                                <span class="error"><?php echo $email_err; ?></span>
                            </div>
                            <div class="form-group mb-3">
                                <label>Message</label>
                                <textarea name="message" class="form-control"><?php echo $message; ?></textarea>
                                <span class="error"><?php echo $message_err; ?></span>
                            </div>
                            <div class="form-group mt-3">
                                <input type="submit" class="btn btn-primary" value="Submit Tip">
                            </div>
                        </form>
                        <?php } else {
                            echo $succ_message;
                        } ?>
                    </div>
                </div>
            </div>
            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>

</html>