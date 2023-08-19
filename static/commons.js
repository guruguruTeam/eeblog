// 保存ajax进行post请求下载
function ajax_download(url, data, $) {
	var $iframe, iframe_doc, iframe_html;
	$('#download_iframe').remove();
	
	// 重新创建iframe
	$iframe = $("<iframe id='download_iframe' style='display: none' src='about:blank'></iframe>").appendTo("body");

	iframe_doc = $iframe[0].contentWindow || $iframe[0].contentDocument;
	if (iframe_doc.document) {
		iframe_doc = iframe_doc.document;
	}

	iframe_html = "<html><head></head><body><form method='POST' action='" + url + "?"+Math.random()+"'>"

	Object.keys(data).forEach(function(key) {
		iframe_html += "<input type='hidden' name='" + key + "' value='" + data[key] + "'>";

	});

	iframe_html += "</form></body></html>";

	iframe_doc.open();
	iframe_doc.write(iframe_html);
	$(iframe_doc).find('form').submit();
}


// 表格默认参数
var $$ = $$ || {};
$$.tbconfig = {
	elem: '#LAY-table',
	even: true,  //开启隔行背景	
	//size: 'sm',  //小尺寸的表格
	height: 'full-180',  //容器高度
	method: 'post',
	page: true, 
	limits: [20, 50, 100, 200], 
	limit: 20,  //默认采用25
	loading: true, 
	autoSort: false
}

$$.ajax = function(cfg) {
	var me = this;	
	$.ajax({
        type: 'post',
        dataType: 'json',
        url: cfg.url,
        data: cfg.data || cfg.param || {},
        async: (typeof cfg.async=='undefined') ? true : cfg.async,	//默认异步
        success: cfg.success || cfg.callback,
        error: cfg.error
    });
}

// 表单单击选中行
$$.selectRow = function() {
	//单击行勾选checkbox事件
    $(document).on("click", ".layui-table-body table.layui-table tbody tr", function () {
        var index = $(this).attr('data-index');
        var tableBox = $(this).parents('.layui-table-box');
        //存在固定列
        if (tableBox.find(".layui-table-fixed.layui-table-fixed-l").length > 0) {
            tableDiv = tableBox.find(".layui-table-fixed.layui-table-fixed-l");
        } else {
            tableDiv = tableBox.find(".layui-table-body.layui-table-main");
        }
        var CheckLength = tableDiv.find("tr[data-index=" + index + "]").find("td div.layui-form-checked").length;
        var checkCell = tableDiv.find("tr[data-index=" + index + "]").find("td div.laytable-cell-checkbox div.layui-form-checkbox I");
        if (checkCell.length > 0) {
            checkCell.click();
        }
    });
 
    $(document).on("click", "td div.laytable-cell-checkbox div.layui-form-checkbox", function (e) {
        e.stopPropagation();
    });
}

$$.formatDate = function() {
	var d = new Date();
	var mon = d.getMonth() + 1;
	var day = d.getDate() + 1;
	if(mon<10) mon = '0' + mon;
	if(day < 10) day = '0' + day;
	return d.getYear() + "-" + mon + "-" + day;
}

