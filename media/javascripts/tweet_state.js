function TweetState() {
  this.__being_edited = {};
}

TweetState.prototype.add_being_edited = function(key, panel_id) {
  this.__being_edited[key] = panel_id;
}

TweetState.prototype.remove_being_edited = function(key) {
  delete this.__being_edited[key];
}

TweetState.prototype.is_being_edited = function(key) {
  return this.__being_edited[key] != null;
}

TweetState.prototype.get_editing_panel_id = function(key) {
  return this.__being_edited[key];
}
