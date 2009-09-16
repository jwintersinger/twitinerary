function DatetimeHumanizer() {
  $('span.datetime').each(function() {
    var self = $(this);
    var ms_since_epoch = 1000*parseInt(self.text(), 10);
    self.text(new Date(ms_since_epoch).toLocaleString());
  });
}
