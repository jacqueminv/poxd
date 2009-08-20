<?php
    header("Content-Type: application/json"); 
    
    $userid = 'poxd';    $key = '2652641547';    $resultsets = 'books,bookdate';    $booksort = 'entry_REV';    $max = 5;    $callback = 'displaybooks';
    $coverheight = 70;
    
    $url = 'http://www.librarything.com/api_getdata.php?';	$url .= 'userid=' . $userid;	$url .= '&key=' . $key;	$url .= '&resultsets=' . $resultsets;	$url .= '&booksort=' . $booksort;	$url .= '&max=' . $max;
	$url .= '&coverheight=' . $coverheight;
    
    // This function initializes CURL, sets the necessary CURL
    // options, executes the request and returns the results.
    function getResource($url){
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            $result = curl_exec($ch);
            curl_close($ch);
    
            return $result;
    }
    
    // Call getResource to make the request.
    $books = getResource($url);
    
    //transforms LibraryThing output towards a JSON response
    $pos = strpos($books, '{');
    if($pos !== false) {
        $books = substr($books, $pos);
        $pos = strripos($books, '}');
        if($pos !== false) {
            $books =   substr($books, 0, ($pos+1));  
        }   
    }
    
    echo $books;
?>