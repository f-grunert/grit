<?php
function write($mode, $name, $content) {
 while (file_exists("lock.tmp")) {
  sleep(0.01);
 }
 touch("lock.tmp");
 $filecontent = file_get_contents("interaction.log")."\n[client:".$mode.":".$name."]\t".$content;
 file_put_contents("interaction.log", $filecontent);
 unlink("lock.tmp"); 
}


if (isset($_POST["mode"]) == false) {
 exit("Parameter 'mode' not set.");
}

if ($_POST["mode"] == "question") {
 if (isset($_POST["name"]) == false) {
  exit("Parameter 'name' not set.");
 }
 if (isset($_POST["question"]) == false) {
  exit("Parameter 'question' not set.");
 }
 write("question", str_replace(["\n","\t"], " ", trim($_POST["name"])), str_replace(["\n","\t"], " ", trim($_POST["question"])));
 exit("true");
}

if ($_POST["mode"] == "service") {
 if (isset($_POST["name"]) == false) {
  exit("Parameter 'name' not set.");
 }
 if (isset($_POST["question"]) == false) {
  exit("Parameter 'question' not set.");
 }
 write("service", str_replace(["\n","\t"], " ", trim($_POST["name"])), str_replace(["\n","\t"], " ", trim($_POST["question"])));
 exit("true");
}
?>