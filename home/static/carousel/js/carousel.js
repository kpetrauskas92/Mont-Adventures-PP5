/* eslint-disable no-undef */
document.addEventListener('DOMContentLoaded', function() {

  var glideInstances = {};

  glideInstances['topTrips'] = new Glide('#top-trips-carousel', {
    type: 'carousel',
    startAt: 0,
    perView: 3,
    breakpoints: {
        1024: {
          perView: 3
        },
        930: {
          perView: 2
        },
        640: {
          perView: 1
        },
    },
    peek: {
        before: 20,
        after: 20
    }
  });
  
  glideInstances['topTrips'].mount();

  glideInstances['country'] = new Glide('#country-carousel', {
    type: 'carousel',
    startAt: 0,
    perView: 4,
    breakpoints: {
        1024: {
          perView: 3
        },
        768: {
          perView: 2
        },
        640: {
          perView: 1
        },
    },
    peek: {
        before: 20,
        after: 20
    }
  });
  
  glideInstances['country'].mount();

});
