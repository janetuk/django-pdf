/*
 * html2pdf.js
 * Originally taken from:
 * http://we-love-php.blogspot.co.uk/2012/12/create-pdf-invoices-with-html5-and-phantomjs.html
 */
var page    = require('webpage').create();
var fs      = require("fs");
var system  = require("system");

// change the paper size to letter, add some borders
// add a footer callback showing page numbers
page.paperSize = {
  format: "Letter",
  orientation: "portrait",
  margin: {left:"2.5cm", right:"2.5cm", top:"1cm", bottom:"1cm"},
  footer: {
    height: "0.9cm",
    contents: phantom.callback(function(pageNum, numPages) {
      return "<div style='text-align:center;'><small>" + pageNum +
        " / " + numPages + "</small></div>";
    })
  }
};

page.zoomFactor = 1.5;

// read contents of page from file
var html = fs.read(system.args[1]);

page.content = html;

// wait until the content has loaded
page.onLoadFinished = function(status) {
    // save output file
    page.render(system.args[2]);
    phantom.exit();
};

