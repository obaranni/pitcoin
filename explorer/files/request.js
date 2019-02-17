(function(){
    var root = this;
    var RequestUtil = null;

    if(typeof exports !== "undefined"){
        RequestUtil = exports;
    } else {
        RequestUtil = root.RequestUtil = {};
    }


    var baseUrl = CommonUtil.getOriginPath();
    var URLS = {
        "GO_BLOCKS"             : baseUrl + "/blocks",
        "GO_BLOCKS_DETAIL"      : baseUrl + "/blocks/detail",
        "GO_TRANSACTION_PAGE"   : baseUrl + "/blocks/transaction",
        "GO_ADDRESS_PAGE"       : baseUrl + "/blocks/address",
        "SEND_FROM"             : baseUrl + "/wallet/sendFrom.json",
        "SEARCH_TEXT"           : baseUrl + "/search"

    };

    RequestUtil.movePage = function(menu, params){
        var requestParams = getRequestParams(menu, params);
        LinkUtil.moveByPost(requestParams);
    };

    RequestUtil.popupPage = function(menu, params){
        var requestParams = getRequestParams(menu, params);
        LinkUtil.popupByPost(requestParams);
    };

    RequestUtil.handleDataByAjax = function(menu, params){
        var requestParams = getRequestParams(menu, params);
        LinkUtil.handleDataByAjax(requestParams);
    };


    var getRequestParams = function (menu, params) {
        var tempParams = {
            url: URLS[menu]
            , target: "_self"
        };

        var requestParams = addHiddenParams(tempParams, params);

        return requestParams;
    };

    var addHiddenParams = function(tempParams, params){

        if(tempParams.hiddenParams === undefined){
            tempParams.hiddenParams = {};
        }
        if(typeof params !== "undefined" && params !== null ) {
            $.each(params, function(key, value){
                if(typeof value !== "function"){
                    tempParams.hiddenParams[key] = value
                } else {
                    tempParams[key] = value
                }
            });
        }
        console.log(tempParams);
        return tempParams;
    };
}());