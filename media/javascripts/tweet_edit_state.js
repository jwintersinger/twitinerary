function TweetEditState() {
  this.__being_edited = {};
}

TweetEditState.prototype.add_being_edited = function(key, panel_id) {
  this.__being_edited[key] = panel_id;
}

TweetEditState.prototype.remove_being_edited = function(key) {
  delete this.__being_edited[key];
}

TweetEditState.prototype.is_being_edited = function(key) {
  return this.__being_edited[key] != null;
}

TweetEditState.prototype.get_editing_panel_id = function(key) {
  return this.__being_edited[key];
}
