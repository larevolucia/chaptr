(function () {
    const header = document.querySelector('.site-header');
    const setHeightVar = () => {
      if (header) document.documentElement.style.setProperty('--header-height', header.offsetHeight + 'px');
    };
    setHeightVar();
    addEventListener('resize', setHeightVar);
  })();
