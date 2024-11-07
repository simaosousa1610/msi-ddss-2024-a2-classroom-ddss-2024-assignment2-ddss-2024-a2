<?php

	if($_SERVER["REQUEST_METHOD"] == "POST") {
		$password = $_POST['v_password'];
		$username = $_POST['v_username'];
		$remember = $_POST['v_remember'];
	} else{
		$password = $_GET['v_password'];
		$username = $_GET['v_username'];
		$remember = $_GET['v_remember'];
	}

    

    print("v_password  -> " . $password . "<br/>");
    print("v_username  -> " . $username . "<br/>");
    print("v_remember  -> " . $remember . "<br/>");





?>

