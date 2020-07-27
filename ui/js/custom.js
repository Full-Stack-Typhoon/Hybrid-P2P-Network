var resultobj = {};
var server_url = "http://localhost:8080/uihandler";
var latestchattime = 0;
$(document).ready(function(){
    $('#dirbutton').click(function(){
	var dir = $('#dirbox').val();
	console.log(dirbox);
	$.ajax({
	    type: "POST",
	    url: server_url,
	    data: { type: "set_dir", data: dir },
	    error: function(e){},
	    success: function(){
		console.log('dir sent');
	    }
	});
    });
    $('#searchbutton').click(function(){
	var searchtext = $('#searchbox').val();
	console.log(searchtext);
	$.ajax({
	    type: "POST",
	    url: server_url,
	    data: { type: "search", data: searchtext },
	    dataType: 'json',
	    error: function(e){
		console.log("Did not receive search result: "+e);
	    },
	    success: function(result){
		console.log(result);
		result = result['data'];
		console.log("received "+result);
		// result = [
		//     { filename : "asd", size: 2, md5sum: "1234uhasduqwei3io", ip: "10.2.3.4" },
		//     { filename : "asd2", size: 12, md5sum: "1234uhasduqwed", ip: "110.2.3.4" },
		//     { filename : "asd3", size: 32, md5sum: "1222222222222qwei3io", ip: "10.2.3.24" },
		//     { filename : "asd4", size: 132, md5sum: "1qwei3io", ip: "10.2.3.44" },
		//     { filename : "asd5", size: 222, md5sum: "1hasduqwei3io", ip: "10.112.3.4" }
		// ];

		// resultobj = {};
		// for(var i = 0; i < result.length; i++) {
		//     resultobj['res_'+i] = result[i];
		// }
		// console.log(resultobj);
		//		$('#searchresult tr').remove()
		$('#searchresult').bootstrapTable('load', result ).on('dbl-click-row.bs.table', function(e, row, $element){
		    var ips = [];
		    $.each(result, function( i, res ){
			if( res['md5sum'] == row['md5sum'] ){
			    ips.push(res['ip']);
			}
		    });

		    var datatosend = { 'file': row, 'ips': ips };
		    $.ajax({
			type: "POST",
			url: server_url,
			data: { type: "get_file", data: JSON.stringify( datatosend )  } ,
			dataType: 'json',
			error: function(){
			    console.log("yyoyoyoy");
			},
			success: function(result){
			    console.log(result);
			    var filepath = '/'+result['f'];
			    console.log('filepath is: '+filepath);
			    play(filepath);
			}
		    });
		}); //('method'), result);
		//		buildHtmlTable(result);
	    }
	});
	// console.log("donenenne");
    });

    receive_chat();

    $('#chatrefresh').click(receive_chat);

    $('#chatsend').click(function(){
	$.ajax({
	    type: "POST",
	    url: server_url,
	    data: { type: "send_chat", data: $('#chatinput').val() },
	    error: function(e){
		console.log(e);
	    },
	    success: receive_chat
	});
    });
});

function receive_chat(){
    $.ajax({
	type: "POST",
	url: server_url,
	data: { type: "receive_chat", data: latestchattime },
	dataType: 'json',
	error: function(e){
	    console.log(e);
	},
	success: function(chats){
	    // chats=[
	    // 	{ message: "asdads asd", timestamp: 2, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 3, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 4, ip: "10.12.2.3"},
	    // 	{ message: "asdads asd", timestamp: 6, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 9, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 14, ip: "10.12.2.3"},
	    // 	{ message: "asdads asd", timestamp: 2, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 3, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 4, ip: "10.12.2.3"},
	    // 	{ message: "asdads asd", timestamp: 6, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 9, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 14, ip: "10.12.2.3"},
	    // 	{ message: "asdads asd", timestamp: 2, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 3, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 4, ip: "10.12.2.3"},
	    // 	{ message: "asdads asd", timestamp: 6, ip: "10.1.2.3"},
	    // 	{ message: "a asd", timestamp: 9, ip: "111.1.2.3"},
	    // 	{ message: "asd asd", timestamp: 14, ip: "10.12.2.3"}
	    // ];
	    console.log("chats receive: "+chats);
	    var maxts = latestchattime;
	    $.each(chats,function(i, chat){
		if( chat['timestamp'] > latestchattime ){
		    var msg = $('<div/>', { 'class': 'panel panel-info' } );
		    var msginfo = $('<div/>', { 'class': 'panel-heading clearfix' } );
		    var msgtxt = $('<div/>', { 'class': 'panel-body' } );
		    var infocnt = $('<div/>');
		    infocnt.append("<div class='' style='float:left'>"+chat['ip']+"</div>");
		    infocnt.append("<div class='' style='float:right'>"+chat['timestamp']+"</div>");
		    //		    msginfo.append(infocnt);
		    msginfo.append("<h2 class='panel-title pull-left'>"+chat['ip']+"</h2>");
		    msginfo.append("<h2 class='panel-title pull-right'>"+chat['timestamp']+"</h2>");

		    msgtxt.append("<p class=''>"+chat['message']+"</p>");

		    msg.append(msginfo);
		    msg.append(msgtxt);
		    $('#chatlog').append(msg);
		    // $('#chatlog').append( "<tr>" + "{ <span class='label label-default'>"+chat['ip']+"</span> }: "+chat['message'] + "</tr>" );
		}
		if( chat['timestamp'] > maxts ){
		    maxts = chat['timestamp'];
		}
	    });
	    latestchattime = maxts
	}
    });
}

function play(filepath)
{
    console.log(filepath)
    var p = document.getElementById('player');
    p.src = filepath;
    p.load();
    p.play();
    $('#player').attr('src', filepath);
    $('#player').load();
    $('#player').play();
}

// function get_file(element)
// {
//     // console.log(element);
//     var ips = [];
//     $.each(resultobj, function( key, res ){
// 	if( res['md5sum'] == resultobj[element.id]['md5sum'] ){
// 	    ips.push(res['ip']);
// 	}
//     });

//     var datatosend = { 'file': resultobj[element.id], 'ips': ips };
//     $.ajax({
//         type: "POST",
//         url: server_url,
//         data: { type: "getfile", data: JSON.stringify(datatosend)  },
//         success: function(){
//             console.log("yyoyoyoy");
//         },
//         error: function(result){
//             filepath = 'BlankSpace.mp3';
//             play(filepath);
//         }
//     });
// }

// // Builds the HTML Table out of myList.
// function buildHtmlTable(myList) {
//     //    var columns = addAllColumnHeaders(myList);

//     for (var i = 0 ; i < myList.length ; i++) {
//         var row$ = $('<tr/>').attr("id", "res_" + i).attr("ondblclick", "get_file(this)");
//         for (var colIndex = 0 ; colIndex < columns.length ; colIndex++) {
//             var cellValue = myList[i][columns[colIndex]];

//             if (cellValue == null) { cellValue = ""; }

//             row$.append($('<td/>').html(cellValue));
//         }
//         $("#searchresult").append(row$);
//     }
// }

// // Adds a header row to the table and returns the set of columns.
// // Need to do union of keys from all records as some records may not contain
// // all records
// function addAllColumnHeaders(myList)
// {
//     var columnSet = [];
//     var headerTr$ = $('<tr/>');

//     for (var i = 0 ; i < myList.length ; i++) {
//         var rowHash = myList[i];
//         for (var key in rowHash) {
//             if ($.inArray(key, columnSet) == -1){
//                 columnSet.push(key);
//                 headerTr$.append($('<th/>').html(key));
//             }
//         }
//     }
//     headerTr$.addClass("info");
//     $("#searchresult").append(headerTr$);

//     return columnSet;
// }
