$(function () {

	//팝업 닫기
	$(".b-close").on("click", function(){
		closePopup();
	});

	//탭
	$(".ttabs").each(function(){
		var $this = $(this);
		var $total = $this.find("li").length;
		var $first = 0;
		var $prev = $first;
		var tab_id = new Array();
		var $btn = $this.find("li");
		var $start = $btn.eq($first);

		for( var i=0; i<$total; i++){
		  tab_id[i] = $btn.eq(i).find("a").attr("href");
		  $(tab_id[i]).css("display","none");
		  $(tab_id[$first]).css("display","block");
		}

		$start.addClass("on");

		$btn.bind("click",function(){
			var $this = $(this);
			var $index = $(this).index();

			if(!$this.hasClass("link")){
				  if(!$this.hasClass("on")){
				   $btn.each(function(){
					$(this).removeClass("on");
				   });
				   $this.addClass("on");
				   $(tab_id[$prev]).css("display","none");
				   $(tab_id[$index]).css("display","block");
				   $prev = $index;
				}
				$this.trigger("resize");

				return false;

			}
		});
	});//each


	//툴팁
	$(".tip_fee").tooltipster({maxWidth : 220});

	//placeholder
	// $('input, textarea').placeholder();



});



function closePopup() {
	$(".popup_wrap").fadeOut(100);
}


//링크
function boxLink(e) {
	var obj = $(e).find("a");
	var link = obj.attr("href");

	window.location.href = link;
}


function getCookie(c_name) {
	var i, x, y, ARRcookies = document.cookie.split(";");
	for (i = 0; i < ARRcookies.length; i++) {
		x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
		y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
		x = x.replace(/^\s+|\s+$/g, "");
		if (x == c_name) {
			return unescape(y);
		}
	}
}

var IS_SUBMIT = false;
var reCAPTCHA_login;
var reCAPTCHA_signup;
var recaptchaResponse;
function recaptchaCheck(opt_widget_id) {
	if (typeof(grecaptcha) != 'undefined') {
		if (grecaptcha.getResponse(opt_widget_id) == "") {
			alert("Confirm you're a human.");
			return false;
		} else {
			recaptchaResponse = grecaptcha.getResponse(opt_widget_id);
			return true;
		}
	} else {
		return false;
	}
}

function goWallet(chaintype, owner) {
    console.log(chaintype + " , " + owner);
    if ("mainnet" === chaintype) {
        if ("wizbl" === owner) {
            var isDownload = confirm("Do you want to move WIZBL Web Wallet page?");
            if (isDownload) {
                var link = document.createElement('a');
                document.body.appendChild(link);
                link.href = "https://wallet.wizbl.io";
                link.click();
            }
        } else if ("wiziix" === owner) {
            var isDownload = confirm("Do you want to move WIZIIX Web Wallet page?");
            if (isDownload) {
                var link = document.createElement('a');
                document.body.appendChild(link);
                link.href = "https://wizblex.io";
                link.click();
            }
        }
    } else {
        console.log("ELSE " + chaintype + " , " + owner);
        $.ajax({
            url: "/ajax/sessioncheck",
            data: {},
            type: "POST",
            dataType: "json",
            timeout: 30000,
            async: false,
            cache: false,
            contentType: "application/x-www-form-urlencoded; charset=UTF-8",
            success: function (response, status, request) {
                console.log(response);
                if (response.result == "success") {
                    location.href = "/wallet";
                } else {
                    showPop("#btn_popup");
                }
            },
            beforeSend: function (xmlHttpRequest) {
                xmlHttpRequest.setRequestHeader("AJAX", "true");
            },
            error: function (response, status, error) {
                showPop("#btn_popup");
            },
            complete: function () {
            }
        });
    }
}

function showPop(id) {
	$('body,html').animate({scrollTop: 0}, 0);
	$(".popup_wrap").hide();
	$(id).show();
}

function showLogin() {
	$("#login_pwd").val('');
	showPop('#login_popup');
	try {
		grecaptcha.reset(reCAPTCHA_login);
	} catch (e) {
		console.log(e);
	}
}
function showSignup() {
	$("#signup_email").val('');
	$("#signup_pwd").val('');
	showPop('#join_popup');
	try {
		grecaptcha.reset(reCAPTCHA_signup);
	} catch (e) {
		console.log(e);
	}
}

var onloadCallback = function() {
	if(header_chaintype != null && header_chaintype === "mainnet"){
		return false;
	} else {
        reCAPTCHA_login = grecaptcha.render('reCAPTCHA_login', {
            'sitekey' : '6LdNqFwUAAAAAMVTGPEn6NqMNkWYZoML4UvJO7V6',
            'theme' : 'dark'
        });
        reCAPTCHA_signup = grecaptcha.render('reCAPTCHA_signup', {
            'sitekey' : '6LdNqFwUAAAAAMVTGPEn6NqMNkWYZoML4UvJO7V6',
            'theme' : 'dark'
        });
	}


};

function logout() {
	if (!confirm("Do you want to logout?")) {
		return;
	}
	$.ajax({
		url: "/ajax/logout",
		data: {},
		type:"POST",
		dataType:"json",
		timeout:30000,
		async:false,
		cache:false,
		contentType:"application/x-www-form-urlencoded; charset=UTF-8",
		success: function(response, status, request) {
			console.log(response);
			if(response.result == "success") {
				location.href = "/";
			}
		},
		beforeSend: function(xmlHttpRequest) {
			xmlHttpRequest.setRequestHeader("AJAX", "true");
		},
		error: function(response, status, error) {
		},
		complete: function() {
		}
	});
}



var mobileW = 841;
function mobileSizeFlag(){
	var wWeight = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
	var flag  = mobileW >= wWeight;

	return flag;
}

