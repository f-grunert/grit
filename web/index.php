<html>
 <head>
  <style>
   body { font-family: sans-serif; }
   input { cursor: pointer; }
   ul {margin: 0; padding: 0; list-style-position: inside; list-style-type: square;}
  </style>
  <script type="text/javascript">
   setInterval(check_stream, 2000);
   
   function check_stream() {
    var http_check = new XMLHttpRequest();
    http_check.open("HEAD", "interaction/stream.tmp", false);
    http_check.send();
    if (http_check.status == 404) {
     document.getElementById("output_streamon").style.display = "none";
     document.getElementById("output_streamoff").style.display = "inline";
     document.getElementById("button_question").disabled = true;
     document.getElementById("button_service").disabled = true;
    } else {
     document.getElementById("output_streamon").style.display = "inline";
     document.getElementById("output_streamoff").style.display = "none";
     document.getElementById("button_question").disabled = false;
     document.getElementById("button_service").disabled = false;
    }
   }
  
   function send_question () {
    // Einlesen der Daten
    var question = document.getElementById("input_question").value;
	var name = document.getElementById("input_name").value;
	if (question == "" || name == "") {
     document.getElementById("output_question").innerHTML = "Bitte geben Sie eine Frage und Ihren Namen ein!<br>";
	 return;
	}
	
    try {
     var userfiles = document.getElementsByName("fileselection");
     userfiles.forEach(function(userfile) {
      if (userfile.checked) {
       question = question + '>>' + userfile.value;
       userfile.checked = false;
      }
     });
    } catch {
     console.log("null");
    }
    
	// Initialisierung HTTP-Anfrage
	if (window.XMLHttpRequest) {
     http_request = new XMLHttpRequest();
    }
	
	// Check Serverstatus
    http_request.onreadystatechange = function() {
     if (http_request.readyState == 4 && http_request.status == 200 && http_request.responseText == "true") {
      document.getElementById("input_question").value = null;
	  document.getElementById("output_question").innerHTML = "Frage<br><i>" + question + "<br></i>gesendet!<br>";
     } else {
      document.getElementById("output_question").innerHTML = "Server-Fehler:<br>readyState: " + http_request.readyState + "<br>status: " + http_request.status + "<br>responseText:" + http_request.responseText;
      return;
	 }
    }
	
	// Senden der Anfrage
	http_request.open("POST", "interaction/agent.php", true);
    http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http_request.send("mode=question&name=" + name + "&question=" + question);
   }
   
   function send_service () {
    // Einlesen der Daten
    var request = document.getElementById("select_service").value;
	var name = document.getElementById("input_servicename").value;
	if (name == "") {
     document.getElementById("output_service").innerHTML = "Bitte geben Sie Ihren Namen ein!<br>";
	 return;
	}   

	// Initialisierung HTTP-Anfrage
	if (window.XMLHttpRequest) {
     http_request = new XMLHttpRequest();
    }
	
	// Check Serverstatus
    http_request.onreadystatechange = function() {
     if (http_request.readyState == 4 && http_request.status == 200 && http_request.responseText == "true") {
	  document.getElementById("output_service").innerHTML = "Serviceanfrage<br><i>" + request + "<br></i>gesendet!";
     } else {
      document.getElementById("output_service").innerHTML = "Server-Fehler:<br>readyState: " + http_request.readyState + "<br>status: " + http_request.status + "<br>responseText:" + http_request.responseText;
      return;
	 }
    }
	
	// Senden der Anfrage
	http_request.open("POST", "interaction/agent.php", true);
    http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http_request.send("mode=service&name=" + name + "&question=" + request);
   }
  </script>
  <?php
#error_reporting(E_ALL | E_STRICT);
#ini_set('display_errors', 1);

   $uploaddir = "/home/pi/Documents/Scripts/";
   
   if (isset($_FILES["uploadfile"])) {
    $file = $_FILES["uploadfile"];
   
    if ($file["error"] !== UPLOAD_ERR_OK) {
     $output_question = "<font color='red'><i>Uploadfehler</i></font><br>";
    }
    
    $name = preg_replace("/[^A-Z0-9._-]/i", "_", $file["name"]);
    
    $i = 0;
    $parts = pathinfo($name);
    while (file_exists($uploaddir . $name)) {
     $i++;
     $name = $parts["filename"] . "-" . $i . "." . $parts["extension"];
    }
    
    $success = move_uploaded_file($file["tmp_name"], $uploaddir.$name);
    if (!$success) {
     $output_question = "<font color='red'><i>Datei konnte nicht gespeichert werden</i></font><br>";
    } else {
     $output_question = "<font color='green'><i>Datei gespeichert; am Ende der Nachricht bitte folgendes eingeben: >>$name</i></font><br>";
     chmod($uploaddir . $name, 0777);
    }
   }

   $response = file_get_contents('https://schueler:zabelhaft@fgrunert.lima-city.de/schule/check.php');
   if ($response == 'ok') {
    $ip = shell_exec('curl ifconfig.me');
   } else {
    $ip = shell_exec('hostname -I');
   }
  ?>
 </head>
 <body onload="check_stream()">
  <h1><u>Live-Partizipation am Unterricht:</u></h1><br>
  <b>Livestream:</b><br>
  <iframe id="output_streamon" src="<?php echo 'http://'.$ip; ?>" style="display:none;" width="50 %" height="60 %" scrolling="no" frameborder="0" allowfullscreen>Stream aktuell nicht verf�gbar</iframe>
  <font color="red"><span id="output_streamoff">Stream derzeit nicht aktiv!</span></font><br><br>
  <b><i>Interaktionen:</i></b><br>
  <u>Frage stellen</u><br>
  Name:<br>
  <input type="text" id="input_name"></input><br><br>
  Frage:<br>
  <textarea id="input_question"></textarea><br><br>
    <?php
$systemfiles = ["capture.gif", "gpio.py", "grunbot.py", "ip.py", "message_notifier.wav", "message_start.wav", "shutdown.py", "sync.ffs_db"];
$userfiles = [];
foreach (scandir("/home/pi/Documents/Scripts/") as $dat) {
 if (is_dir("/home/pi/Documents/Scripts/".$dat) != true and in_array($dat, $systemfiles) == false and $dat[0] != '.') {
  array_push($userfiles, "/home/pi/Documents/Scripts/".$dat);
 }
}
if ($userfiles != []) {
 echo "Dateireferenz (optional):<br>";
 $i = 0;
 foreach ($userfiles as $userfile) {
  echo "<input type='radio' name='fileselection' id='fileselection$i' value='".$userfile."'><img src='".$userfile."'></img> ".end(explode("/", $userfile))."</input><br>";
  $i++;
 }
 echo "<br>";
}
  ?>
  <button onclick="send_question()" id="button_question">Absenden</button><br><br>
  
  Bilddatei (optional):<br>
  <form action="index.php" method="post" enctype="multipart/form-data"> 
   <input type="file" name="uploadfile">
   <input type="submit" value="Absenden">
  </form>
  
  <font color="red"><span id="output_question"><?php if (isset($output_question)) {echo $output_question;} ?></span></font><br>
  
  <u>Lehrerdateien</u><br>
  <?php
if (is_dir("interaction/usblink")) {
 $usbcontent = scandir("interaction/usblink");
 if (count($usbcontent) > 2) {
  echo "<ul>";
  foreach ($usbcontent as $usbfile) {
   if (is_file("interaction/usblink/$usbfile")) {
    echo "<li><a href='interaction/usblink/$usbfile'>$usbfile</a></li>";
   }
  }
  echo "</ul>";
 } else {
  echo "<i>keine Daten vorhanden</i><br>";
 }
} else {
 $usbdevices = scandir("/media/pi");
 foreach ($usbdevices as $device) {
  if (is_dir("/media/pi/$device") and $device != "." and $device != "..") {
   $usbpath = "/media/pi/$device";
   break;
  }
 }
 if (isset($usbpath) and is_dir("$usbpath/GRIT/") and count(scandir("$usbpath/GRIT")) > 2) {
  unlink("interaction/usblink");
  symlink("$usbpath/GRIT/", "interaction/usblink");
  echo "<ul>";
  foreach (scandir("interaction/usblink") as $usbfile) {
   if (is_file("interaction/usblink/$usbfile")) {
    echo "<li><a href='interaction/usblink/$usbfile'>$usbfile</a></li>";
   }
  }
  echo "</ul>";
 } else {
  unlink("interaction/usblink");
  echo "<i>kein USB-Ger&auml;t des Lehrers angeschlossen</i><br>";
 }
}
  ?><br>
  
  <u>Serviceanfrage</u><br>
  Name:<br>
  <input type="text" id="input_servicename"></input><br><br>
  Anfrage:<br>
  <select id="select_service">
   <option value="Aktivierung des Lichts">Aktivierung des Lichts</option>
   <option value="Deaktivierung des Lichts">Deaktivierung des Lichts</option>
   <option value="Verschiebung der Tafel">Verschiebung der Tafel</option>
   <option value="Positionsver�nderung der Lehrkraft">Positionsver&auml;nderung der Lehrkraft</option>
 </select><br><br>
 <button onclick="send_service()" id="button_service">Absenden</button><br>
 <font color="red"><span id="output_service"></span></font><br>
 </body>
</html>
