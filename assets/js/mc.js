// Shared Monte Carlo helpers for the retirement pages (seeded, so the same inputs always give the same answer).
//
//   MC.forEachPath({ years, trials, ret, vol, seed }, rets => { ... });   rets[i] = return of year i+1 (fraction); the array is reused between calls
//   MC.percentile(sortedArray, 0.5)     MC.sortedCopy(array)
//
// Yearly returns are log-normal with the requested arithmetic mean (ret, %) and standard deviation (vol, %), independent across years.
window.MC = (function(){
  const SEED = 20060301;
  const TRIALS = 4000;

  function mulberry32(a){
    return function(){
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function normalSource(rand){
    return function(){
      let u = 0;
      while(u === 0) u = rand();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rand());
    };
  }

  function forEachPath(o, cb){
    const m = o.ret / 100, s = o.vol / 100;
    const sigma2 = Math.log(1 + (s * s) / ((1 + m) * (1 + m)));
    const mu = Math.log(1 + m) - sigma2 / 2;
    const sigma = Math.sqrt(sigma2);
    const normal = normalSource(mulberry32(o.seed === undefined ? SEED : o.seed));
    const trials = o.trials || TRIALS;
    const rets = new Float64Array(o.years);
    for(let k = 0; k < trials; k++){
      for(let i = 0; i < o.years; i++) rets[i] = Math.exp(mu + sigma * normal()) - 1;
      cb(rets);
    }
  }

  function percentile(sorted, q){
    const pos = (sorted.length - 1) * q;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }

  function sortedCopy(arr){
    const a = Float64Array.from(arr);
    a.sort();
    return a;
  }

  return { SEED, TRIALS, forEachPath, percentile, sortedCopy };
})();
