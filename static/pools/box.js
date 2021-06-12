
// LatLng -> Point
var fromLatLngToPixelCoordinates = function (latLng) {
  var numTiles = 1 << map.getZoom();
  var projection = new MercatorProjection();
  var worldCoordinate = projection.fromLatLngToPoint(latLng);
  var pixelCoordinate = new google.maps.Point(
      Math.floor(worldCoordinate.x * numTiles),
      Math.floor(worldCoordinate.y * numTiles));

  return pixelCoordinate;
};

// Point -> LatLng
var fromPixelCoordinatesToLatLng = function (point) {
  var numTiles = 1 << map.getZoom();
  var projection = new MercatorProjection();

  var worldCoordinate = new google.maps.Point(point.x * 1.0 / numTiles, point.y * 1.0 / numTiles);
  return projection.fromPointToLatLng(worldCoordinate);
};

// Bounds -> {x:int, y:int, w:int, h:int}
var fromBoundsToXYWH = function (bounds) {

    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    var nw = new google.maps.LatLng(ne.lat(), sw.lng());
    var se = new google.maps.LatLng(sw.lat(), ne.lng());

    var pixelCoordinates = {
      nw: fromLatLngToPixelCoordinates(nw),
      ne: fromLatLngToPixelCoordinates(ne),
      sw: fromLatLngToPixelCoordinates(sw),
      se: fromLatLngToPixelCoordinates(se)
    };

    return {
      x: pixelCoordinates.nw.x,
      y: pixelCoordinates.nw.y,
      w: pixelCoordinates.ne.x - pixelCoordinates.nw.x, 
      h: pixelCoordinates.se.y - pixelCoordinates.ne.y
    };
};

// {x: y: w: h:} -> Bounds
var fromXYWHToBounds = function (xywh) {
  var topUpperLeft = fromBoundsToXYWH(map.getBounds());

  //in world/pixel coordinate
  var sw = {
    x: topUpperLeft.x + xywh.x,
    y: topUpperLeft.y + xywh.y + xywh.h
  };

  var ne = {
    x: topUpperLeft.x + xywh.x + xywh.w,
    y: topUpperLeft.y + xywh.y 
  };

  return new google.maps.LatLngBounds(fromPixelCoordinatesToLatLng(sw), fromPixelCoordinatesToLatLng(ne));
};

// LatLng {width: height} -> Bounds
var calcBounds = function (center,size) {

  const nsew = {
    north: google.maps.geometry.spherical.computeOffset(center, size.height/2, 0).lat(),

    south: google.maps.geometry.spherical.computeOffset(center, size.height/2, 180).lat(),

    east: google.maps.geometry.spherical.computeOffset(center, size.width/2, 90).lng(),

    west: google.maps.geometry.spherical.computeOffset(center, size.width/2, 270).lng()
  };
  console.log('nsew', nsew);

  return nsew;
};
