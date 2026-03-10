function hideOverlappingLabels() {
  const labels = Array.from(
    document.querySelectorAll('.marker__label--below')
  );

  labels.forEach(el => el.style.visibility = '');

  for (let i = 0; i < labels.length - 1; i++) {
    if (labels[i].style.visibility === 'hidden') continue;

    for (let j = i + 1; j < labels.length; j++) {
      if (labels[j].style.visibility === 'hidden') continue;

      const a = labels[i].getBoundingClientRect();
      const b = labels[j].getBoundingClientRect();

      if (a.right + 4 > b.left) {
        labels[i].style.visibility = 'hidden';
        break;
      }
    }
  }
}


document.addEventListener('DOMContentLoaded', hideOverlappingLabels);
window.addEventListener('resize', hideOverlappingLabels);
