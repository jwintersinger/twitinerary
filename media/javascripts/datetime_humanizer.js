function DatetimeHumanizer() {
  $('.datetime').each(function() {
    var self = $(this);
    var contents = self.text();
    if(!contents.match(/^\d+$/)) return;

    var ms_since_epoch = 1000*parseInt(contents, 10);
    self.text(new Date(ms_since_epoch).toLocaleString());
  });
}
