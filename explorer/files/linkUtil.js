(function () {
    var root = this;
    var LinkUtil = null;

    if(typeof exports !== "undefined"){
        LinkUtil = exports;
    } else {
        LinkUtil = root.LinkUtil = {}
    }

    LinkUtil.moveByPost = function(params){
        var form = document.createElement("form"),
            url = params.url,
            hiddenParams = params.hiddenParams;
        console.log(url);
        if(hiddenParams !== undefined || hiddenParams !== null){
            $.each(hiddenParams, function(key, value){
                form.appendChild(createHidden(key, value));
            });
        }
        form.target = params.target;
        form.action = url;
        form.method = "post";
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    };

    LinkUtil.popupByPost = function(params){
        var form = document.createElement("form"),
            url = params.url,
            target = params.target,
            option = params.option,
            hiddenParams = params.hiddenParams;

        if(hiddenParams !== undefined || hiddenParams !== null ){
            $.each(hiddenParams, function(key, value){
                form.appendChild(key, value);
            })
        }
        form.target = params.target;
        form.action = url;
        form.method = "post";
        document.body.appendChild(form);

        var popup = window.open("", target, option);
        popup.focus();
        form.submit();

        document.body.removeChild(form);

        return popup;
    };


    var IS_SUBMIT = false;
    LinkUtil.handleDataByAjax = function(params){

        if (IS_SUBMIT) {
            alert("Already running. Please wait a moment.");
            return;
        }

        IS_SUBMIT = true;
        $.ajax({
            url: params.url,
            data: params.hiddenParams,
            type:"POST",
            dataType:"json",
            timeout:30000,
            async:false,
            cache:false,
            contentType:"application/x-www-form-urlencoded; charset=UTF-8",
            success: function(response, status, request) {
                console.log(response);
                params.successFtn(response);
                // if (response.result == "success") {
                //     alert("An authentication email has been sent. Please check your email.");
                //     closePopup();
                //     $("#signup_email").val('');
                //     $("#signup_pwd").val('');
                // } else {
                //     alert(response.message);
                // }
            },
            beforeSend: function(xmlHttpRequest) {
                xmlHttpRequest.setRequestHeader("AJAX", "true");
            },
            error: function(response, status, error) {
                console.log(response);
                alert(response.message);
            },
            complete: function() {
                console.log("complete");
                IS_SUBMIT = false;
            }
        })
    };

    function createHidden(key,value) {
        var obj=document.createElement("input");
        obj.type="hidden";
        obj.name=key;
        obj.value=value;
        return obj;
    }
}());