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
