$(document).ready(function(){
    $body = $("body");

    $(document).on({
        ajaxStart: function() { $body.addClass("loading");    },
         ajaxStop: function() { $body.removeClass("loading"); }    
    });

    var viewModel = {
        domains: ["hotel", "electronics"],
        languages: ["es", "en"],
        reviews: ko.observableArray([]),
        selectedDomain: ko.observable("hotels") ,
        selectedLanguage: ko.observable("es") ,
    };

    viewModel.selectedLanguage.subscribe(function(newValue) {
      get_cloud();
    });

    viewModel.selectedDomain.subscribe(function(newValue) {
      get_cloud();
    });


    ko.applyBindings(viewModel);

    function loadReviews(filter){
      $.ajax({
        url: "/reviews/"+viewModel.selectedLanguage()+"/"+viewModel.selectedDomain()+'?filter='+filter,
        dataType: "json"
      })
      .done(function( data ) {
          viewModel.reviews(data);
          console.log(data);
          console.log("Finished loading reviews");
      });

    }

    var sideSize = 600;
    var fill = d3.scale.category20();


    function draw(words) {
      d3.select("#vis").append("svg")
          .attr("width", sideSize)
          .attr("height", sideSize)
        .append("g")
          .attr("transform", "translate(300,300)")
        .selectAll("text")
          .data(words)
        .enter().append("text")
          .style("font-size", function(d) { return d.size + "px"; })
          .style("font-family", "Impact")
          .style("fill", function(d, i) { return fill(i); })
          .attr("text-anchor", "middle")
          .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
          })
        .on("click", function(d) {
          loadReviews(d.text);
        })
        .style("opacity", 1e-6)
      .transition()
        .duration(3000)
        .style("opacity", 1)
          .text(function(d) { return d.text; });
    }

    function get_cloud(){
        viewModel.reviews([]);
        $("#vis").empty();
         $.ajax({
           url: "/anchors/"+viewModel.selectedLanguage()+"/"+viewModel.selectedDomain(),
           dataType: "json"
         })
           .done(function( data ) {
             <!--var ratio = sideSize/((parseInt(data[0].count)-parseInt(data[data.length].count));-->
             var max = data[0].count;
             var median = data[~~(data.length/2-1)].count;
             var min = data[data.length-1].count;
             var ratio = sideSize/(max-min);
             d3.layout.cloud().size([sideSize, sideSize])
                 .words(data.map(function(d) {
                   return {text: d.anchor, size: ratio*(d.count-min)};
                 }))
                 .padding(5)
                 .rotate(function() { return ~~(Math.random() * 2) * 60; })
                 .font("Impact")
                 .fontSize(function(d) { return d.size; })
                 .on("end", draw)
                 .start();
           console.log("Finished loading anchors", data);
         });
   }
});
