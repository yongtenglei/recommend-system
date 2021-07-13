// function drawItems(jsonTexts) {
//   txt = '<div>';
//   for (var i in jsonTexts) {
//     var jsonText = jsonTexts[i];
//     txt += '<ul class="list-group">' + 
//     '<li class="list-group-item">' +
//       '<a href="/item/' + jsonText["categories"] + '/' + jsonText["item id"] + '">' +
//         '<img src="' + jsonText["imgurl"] + '" >' +
//       '</a>' +
//     '</li>' + 
//     '<li class="list-group-item">' +
//         '<p>Name : ' + jsonText["title"] + '</p>' +
//         '<p><span>price :' + jsonText["price"] + '</span></p>' +
//         '<p><span>MLU_CTR: </span><span>' + jsonText["MLU_CTR"] + '</span></p>' +
//         '<p><span>CPU_CTR: </span><span>' + jsonText["CPU_CTR"] + '</span></p>' +
//     '</li>' +
//     '</ul>';
//   }
//   txt += '</div>';
//   document.getElementById("showpicture").innerHTML = txt;
//   $('#waterfall').waterfall();

// }





 // <ul class="list-group">
 //        <li class="list-group-item">
 //          <a href="javascript:;">
 //            <img src="images/1.jpg" />
 //          </a>
 //        </li>
 //        <li class="list-group-item">
 //          <button type="button" class="btn btn-default btn-xs" title="thumb up"><span class="glyphicon glyphicon-thumbs-up"></span></button>
 //          <button type="button" class="btn btn-default btn-xs" title="thumb down"><span class="glyphicon glyphicon-thumbs-down"></span></button>
 //          <button type="button" class="btn btn-default btn-xs pull-right" title="pin"><span class="glyphicon glyphicon-pushpin"></span></button>
 //        </li>
 //        <li class="list-group-item">
 //          <div class="media">
 //            <div class="media-left">
 //              <a href="javascript:;">
 //                <img class="media-object img-rounded" style="width: 30px; height: 30px;" src="images/avatar_30.png" />
 //              </a>
 //            </div>
 //            <div class="media-body">
 //              <h5 class="media-heading">Liber</h5>
 //              <small>I love this pin!</small>
 //            </div>
 //          </div>
 //        </li>
 //      </ul>



function drawItems(jsonTexts) {
  txt = '<div id="row">';
  for (var i in jsonTexts) {
    var jsonText = jsonTexts[i];
    txt += 
    '<div id="col">' +
      '<div id="context_image">' +
        '<a href="/item/' + jsonText["categories"] + '/' + jsonText["item id"] + '">' +
          '<img src="' + jsonText["imgurl"] + '" width="300" height="400">' +
        '</a>' +
        '<div id=context_name class="caption center">' +
          '<p>Name : ' + jsonText["title"] + '</p>' +
         '</div>' +
         '<div id=context_price>' +
          '<p><span>price :' + jsonText["price"] + '</span></p>' +
          '<p><span>MLU_CTR: </span><span>' + jsonText["MLU_CTR"] + '</span></p>' +
          '<p><span>CPU_CTR: </span><span>' + jsonText["CPU_CTR"] + '</span></p>' +
        '</div>' +
      '</div>' +
    '</div>' 
  }
  txt += '</div>'
  document.getElementById("showpicture").innerHTML = txt; 
}

function sendRestfulGet(url) {
  console.log(url)
  var httprequest = new XMLHttpRequest();
  httprequest.open('GET', url, true);
  httprequest.send();
  httprequest.onreadystatechange = function () {
    if (httprequest.readyState == 4 && httprequest.status == 200) {
      drawItems(eval(httprequest.responseText));
    }
  };
}

function sendRecommend(itemid) {
  var result = sendRestfulGet("/recommend/" + itemid)
}
function sendGuessYouLike() {
  var result = sendRestfulGet("/guessyoulike")
}
