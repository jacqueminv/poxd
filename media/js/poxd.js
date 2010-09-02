var poxd = {
    forum_key: "iwdK7RuAjLY7xGZTSZZvZ3lprsY8SplSsI75eb09giEKHNh2ilyRMKHHEHFUPG4C",
    checkEnter: function(e){
        var characterCode;
    	 if(e && e.which) {
    	    e = e;
            characterCode = e.which;
    	 } else {
    	   e = event;
    	   characterCode = e.keyCode;
    	 }	 
    	 if(characterCode == 13) {
     	  document.forms[0].submit()
     	  return false;
    	 }
        return true;
    },
    scrollToTop: function() {
	$('html, body').animate({scrollTop:0}, 'slow');
    }
}