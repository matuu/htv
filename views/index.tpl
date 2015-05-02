<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Formulario para subir archivos">
    <meta name="author" content="Matias Varela">

    <title>Hashtag Viewers</title>
    <!-- Bootstrap Core CSS -->
    <link href='http://fonts.googleapis.com/css?family=Josefin+Sans|Pacifico' rel='stylesheet' type='text/css'>
    <link href="../static/css/bootstrap.min.css" rel="stylesheet" type="text/css">
    <link href="../static/css/style.css" rel="stylesheet">

</head>

<body id="page-top" data-spy="scroll" data-target=".navbar-custom">
    <!--nav class="navbar navbar-default" role="navigation">
        <div class="container">
            <div class="navbar-header page-scroll">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-main-collapse">
                    <i class="fa fa-bars"></i>
                </button>
                <a class="navbar-brand" href="/">
                    <i class="fa fa-play-circle"></i>  INICIO
                </a>
            </div>
        </div>
    </nav-->

    <div class="container">

        <div class="busqueda">
            <h1>¿Qué pasa en Twitter?</h1>
            <input id="hashtag" class="form-control buscar" value="#tuHashTag" />
            <button class="btn btn-success" id="iniciar">Muestrame</button>
        </div>

        <div class="info" style="display:none">
            <h2 id="ht-select"></h2>
            <button class="btn btn-danger" id="detener">Detener</button>

            <div class="row" id="tweets">

            </div>
         </div>
    </div>


        <div class="tweet col-md-12" id="template" style="display:none">

            <div class="user">
                <img class="img-responsive img-thumbnail img-profile"  src=""/>
                <div class="user-text"></div>
                <div class="user-name"></div>
                <div class="meta">
                    <span class="fecha"></span>
                    <span class="retweet"></span>
                    <span class="fav"></span>
                </div>
            </div>
            <div class="text"></div>

        </div>


    <!-- Core JavaScript Files -->
    <script src="../static/js/jquery-1.10.2.js"></script>
    <script src="../static/js/bootstrap.min.js"></script>
    <script type="text/javascript">
            String.prototype.linkify_tweet = function() {
                var tweet = this.replace(/(^|\s)@(\w+)/g, "$1@<a href='http://www.twitter.com/$2'>$2</a>");
           return tweet.replace(/(^|\s)#(\w+)/g, "$1#<a href='http://search.twitter.com/search?q=%23$2'>$2</a>");
         };
    </script>

    <script type="text/javascript">

        ws = new WebSocket("ws://0.0.0.0:8080/update");
        detener = false;
        lastTimeout = 3000;
        (function($){

            $(document).ready(function() {
                $("#detener").prop('disabled', true);
                $("#iniciar").prop('disabled', false);
                $("#hashtag").prop('disabled', false);

                $("#iniciar").click(function(e){
                    e.preventDefault();
                    $("#tweets").empty();
                    ws.send($("#hashtag").val());
                    $(this).prop('disabled', true);
                    $("#hashtag").prop('disabled', true);
                    $("#detener").prop('disabled', false);
                    $("#ht-select").html("Participa con el hashtag <span>" + $("#hashtag").val() + "</span>");
                    detener = false;
                    $(".busqueda").slideUp();
                    $(".info").fadeIn();
                });

                $("#detener").click(function(e){
                    e.preventDefault();
                    detener = true;
                    $(this).prop('disabled', true);
                    $("#hashtag").prop('disabled', false);
                    $("#iniciar").prop('disabled', false);
                    $(".info").fadeOut();
                    $(".busqueda").slideDown();
                });

                ws.onmessage = function(evt) {
                    try {
                        var arr = JSON.parse(evt.data);
                        lastTimeout = (arr.length * 3000) + 3000;
                        var ip;
                        for(ip=0; ip < arr.length; ip+=1) {
                             try {
                                var j = JSON.parse(arr[ip]);
                                //console.log(j);
                                publicador(j, 3000 * ip);

                            } catch (e){
                                console.log(e);
                            }
                       }


                    } catch(e) {
                        console.log(e);
                    }
                    setTimeout(function() {
                        if(detener) return;
                        ws.send($("#hashtag").val());
                    }, lastTimeout);
                };

                function publicador(json, timeout) {
                if (detener) return;
                setTimeout(function() {
                    var $temp = $("#template").clone();
                    $temp.attr("id", "");
                    $temp.find(".user-text").html("<strong>" + json["user"]["name"]+ "</strong>");
                    var str =  "@" +  json["user"]["screen_name"] ;
                    if (json["user"]["location"] != undefined) {
                        str+= " (" + json["user"]["location"] + ")";
                    }
                    $temp.find(".user-name").html(str);
                    $temp.find(".img-profile").attr("src", json["user"]["profile_image_url"]);
                    $temp.find(".text").html(json["text"].linkify_tweet());
                    $temp.find(".fecha").html(new Date(json["created_at"]).toLocaleDateString() + " " + new Date(json["created_at"]).toLocaleTimeString());
                    if(json["retweet_count"] != undefined)
                        $temp.find(".retweet").html("<strong>RT: " + json["retweet_count"]+ "</strong>");
                    $temp.hide();
                    //console.log("Time ->" + timeout);
                    $("#tweets").prepend($temp);
                    $temp.fadeIn(500);
                }, timeout);


            }


            }); // end- document.ready



        })(jQuery);
    </script>


</body>

</html>
