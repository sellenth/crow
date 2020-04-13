pw = ''
entry = document.getElementById("entry");

const scr1 = document.getElementById("scr_1");
const scr2 = document.getElementById("scr_2");


if (getCookie("username") == "") {
  scr2.style.display = "none";
  scr1.style.display = "block";
} else {
  scr1.style.display = "none";
  scr2.style.display = "block";
}

function update_cookie() {
  let username = document.getElementById("i_username").value;
  document.cookie = "username=" + username + "; expires=Thu, 18 Dec 2020 12:00:00 UTC";
  scr1.style.display = "none";
  scr2.style.display = "block";
  return true;
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function check_complete() {
  if (pw.length >= 3) {
    var http = new XMLHttpRequest();
    var url = '/auth';
    http.open('POST', url, true);

    //Send the proper header information along with the request
    http.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    http.send(JSON.stringify({"pw": pw}));

    pw = '';
    clr();
  }
}

function style_btn_press(btn) {
  btn.style.boxShadow = "-2px -2px 12px 0 rgba(255,255,255,.5), 2px 2px 12px 0 rgba(0,0,0,.03)";
  btn.style.fontSize = "3.7em";
  btn.style.color = "grey";
  setTimeout(function () {
    btn.style.boxShadow = "-6px -6px 12px 0 rgba(255,255,255,.5), 12px 12px 12px 0 rgba(0,0,0,.03)";
    btn.style.fontSize = "4em";
    btn.style.color = "black";
  }, 250);
}

function enter(i) {
  btn = document.getElementById(i);
  style_btn_press(btn);
  pw += i.toString();
  entry.innerHTML += '*'
  check_complete();
  return 1;
}

function clr() {
  btn = document.getElementById("clr");
  style_btn_press(btn);
  entry.innerHTML = '';
  pw = '';
  return 1;
}
