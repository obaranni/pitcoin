(function(){
    var root = this;
    var CommonUtil = null;

    if(typeof exports !== "undefined"){
        CommonUtil = exports;
    } else {
        CommonUtil = root.CommonUtil = {};
    }

    CommonUtil.getWebSocketType = function(){
        var webSocketType = (location.protocol === "https") ? "wss://" : "ws://";

        return webSocketType;
    };

    CommonUtil.getContextPath = function(){
        var offset = location.href.indexOf(location.host) + location.host.length;
        var ctxPath = location.href.substring(offset, location.href.indexOf("/", offset+1));
        return ctxPath;
    };

    CommonUtil.getOriginPath = function(){
        return location.origin;
    }

}());