
function createCORSRequest(method, url) {
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {
    xhr.open(method, url, true);
  } else if (typeof XDomainRequest != "undefined") {
    xhr = new XDomainRequest();
    xhr.open(method, url);
  } else {
    xhr = null;
  }
  return xhr;
}

function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
  return time;
}

function createElementFromHTML(htmlString) {
  var tr = document.createElement('td');
  tr.innerHTML = htmlString.trim();

  // Change this to div.childNodes to support multiple top-level nodes
  return tr;
}

function getTxsIds(id){
  i = 0;
  var url = 'http://127.0.0.1:5000/block/txs?id=' + block['id']
  var xhr = createCORSRequest('GET', url)
  xhr.onload = function() {
    if (xhr.readyState === 4 && xhr.status == 200) {
      var text = xhr.responseText;
      txs = JSON.parse(text);
      document.querySelectorAll('.tx_list').forEach(el => el.remove());
      while (i < txs['txs'].length) {
        var new_tr = document.createElement('tr')
        new_tr.setAttribute("class", "tx_list");
        console.log(txs['txs'][i])
        new_tr.innerHTML = 
        '<th scope="row">' + 'tx id: ' + i + '</th> <td id="tx"><a onclick="selectTx(\'' + txs['txs'][i] + '\');">' + txs['txs'][i] + '</a></td>'
        document.getElementById('txs_list').appendChild(new_tr)
        i += 1;
      }
    }
  };
  xhr.onerror = function() {
    alert('Woops, there was an error making the request.');
  };
  xhr.send();
}

function getDeserTx(tx_id){
  i = 0;
  var url = 'http://127.0.0.1:5000/block/txs/deser?tx_id=' + tx_id
  var xhr = createCORSRequest('GET', url)
  xhr.onload = function() {
    if (xhr.readyState === 4 && xhr.status == 200) {
      var text = xhr.responseText;
      deserTx = JSON.parse(text);
      console.log(deserTx)
      openTransaction(deser_tx)
    }
  };
  xhr.onerror = function() {
    alert('Woops, there was an error making the request.');
  };
  xhr.send();
}

function openBlock(id)
{
  // id -= 1;
  var json_str = localStorage.getItem('bb');
  var blocks = JSON.parse(json_str);
  block = blocks[id];
  document.getElementById("currentBlocknumber").innerHTML = parseInt(block['id']);
  if (block['id'] == 0) {document.getElementById("prevBlocknumber").innerHTML = "-"}
  else {document.getElementById("prevBlocknumber").innerHTML = `#${parseInt(block['id'] - 1)}`}
  console.log(block['id'], blocks.length)
  if (block['id'] == blocks.length - 1) {document.getElementById("nextBlocknumber").innerHTML = "-"}
  else {document.getElementById("nextBlocknumber").innerHTML = `#${parseInt(block['id']) + 1}`}
  document.getElementById("currentBlockHash").innerHTML = block.hash
  document.getElementById("prevBlockhash").innerHTML = block.prev_hash
  document.getElementById("date").innerHTML = timeConverter(block.timestamp)
  document.getElementById("size").innerHTML = JSON.stringify(block).length
  document.getElementById("transactions").innerHTML = block["transactions"].length

  getTxsIds(id)
}

function selectBlock(id){
  openBlock(parseInt(id))
}

function openTransaction(deser_tx, tx_id){
  console.log("asdfasdf", deser_tx, tx_id)
  
}

function selectTx(tx_id){
  deser_tx = getDeserTx(tx_id)
}

function setBlocks(blocks)
{  
      var content_div = document.getElementsByClassName("container wrap_main")[0];
      var blocks_len_div = content_div.getElementsByClassName("contents inr-c")[0];
      var jj = blocks_len_div.getElementsByClassName("main_right")[0];
      var jojo = jj.getElementsByClassName("tbl_style1 box-group")[2];
      var lala = jojo.getElementsByClassName("tbl_basic list mtbl_main")[0];
      var lets = lala.getElementsByClassName("let's")[0];
      var goGeronimo = lets.getElementsByClassName("go Geronimo")[0];

      i = 0
      blocks.reverse() 
      while (i < blocks.length) {
        obj = blocks[i]
        var newElement = document.createElement("tr")
        newElement.appendChild(
          createElementFromHTML('<td class="num ta-c" id="block_no_90517"><a href="#area_blocks_detail" onclick="selectBlock('
                   + (parseInt(obj.id)) + ');" class="link">' + (parseInt(obj.id)) + '</a></td>')
        )
        newElement.appendChild(
          createElementFromHTML('<td class="sub" id="block_hash_90517"><span class="t-dot">' + obj["hash"] + '</span></td>')
        )
        newElement.appendChild(
          createElementFromHTML('<td class="tx_S ta-c" id="block_size_90517">' + JSON.stringify(blocks[i]).length + '</td>')
        )
        newElement.appendChild(
          createElementFromHTML('<td class="tx_D" id="block_date_90517">' + timeConverter(obj.timestamp) + '</td>')
        )
        newElement.appendChild(
          createElementFromHTML('<td class="tx_T ta-c" id="block_txs_90517">' + obj["transactions"].length + '</td>')
        )
        goGeronimo.appendChild(newElement)
        i += 1
      }
}

function sleep(miliseconds) {
  var currentTime = new Date().getTime();

  while (currentTime + miliseconds >= new Date().getTime()) {
  }
}

function fetchBlock(i, blocks_count){
  var url = 'http://127.0.0.1:5000/block?height=' + i;
  var xhr = createCORSRequest('GET', url);
  xhr.onload = function() {
    if (xhr.readyState === 4 && xhr.status == 200) {
      var text = xhr.responseText;
      bb.push(JSON.parse(text)['block']);
      blockStr = JSON.stringify(JSON.parse(text)['block']);
        if (i == blocks_count) {
        // var json_str = JSON.stringify(bb);
        // createCookie('blocks', json_str);          
        localStorage.setItem('bb', JSON.stringify(bb));
        setBlocks(bb);
      }
      else {
        fetchBlock(i + 1, blocks_count);
      }
    }
  };
  xhr.onerror = function() {
    alert('Woops, there was an error making the request.');
  };
  xhr.send();
}

function fetchBlocks(blocks_count){
  fetchBlock(1, blocks_count);
}

function fillTableWithBlocks(blocks_count){
  fetchBlocks(blocks_count)
}

function getChainLen(){
  var url = 'http://127.0.0.1:5000/chain/length';
  var xhr = createCORSRequest('GET', url);
  xhr.onload = function() {
    var text = xhr.responseText;
    console.log(text);
    var obj = JSON.parse(text);
    var content_div = document.getElementsByClassName("container wrap_main")[0];
    var blocks_len_div = content_div.getElementsByClassName("contents inr-c")[0];
    var jj = blocks_len_div.getElementsByClassName("main_block box-group")[0];
    var jojo = jj.getElementsByClassName("b1")[0];
    jojo.getElementsByClassName("t")[0].innerHTML = '<strong>' + obj.chain_length + '</strong>'
    fillTableWithBlocks(obj.chain_length)
  };
  xhr.send();
}



var bb = [];
getChainLen();
