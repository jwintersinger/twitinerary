function TweetState() {
  this.__being_edited = {};
}

TweetState.prototype.add_being_edited= function(key) {
  this.__being_edited[key] = true;
}

TweetState.prototype.remove_being_edited = function(key) {
  delete this.__being_edited[key];
}

TweetState.prototype.is_being_edited = function(key) {
  return this.__being_edited[key] != null;
}
