(function(){
    var $ = YAHOO.util.Dom.get;
    var url = 'http://www.poxd.org/server/LT.php';
    var LT = {
	init: function(){
            var callback = {success: displaybooks, failure: error};
	    YAHOO.util.Connect.asyncRequest('GET', url, callback);
	},
	displaybooks: function(r){
            try {
		var result = YAHOO.lang.JSON.parse(r.responseText);
	    } catch(e) {
		return; //silently returns
	    }
	    	    
	    if(result.hasOwnProperty('books')) {
		for(var book in result.books) {
		    book = result.books[book];
		    var title = book.title || '';
		    var author = book.author_lf || '';
		    var cover = book.cover || '';

		    if(cover.length > 0){
			var img = document.createElement('IMG');
			img.setAttribute('src', cover);
			img.src = cover;

			$('readings').appendChild(img);
		    }
		}
	    }
	}};

    var displaybooks = function(response){
	LT.displaybooks(response);
    }

    var error = function(response) {
	
    }

    YAHOO.util.Event.onDOMReady(LT.init);
})();


