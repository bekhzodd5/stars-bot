/**
 * =========================================================================
 * 🌟 STARBOZOR ® - TELEGRAM PREMIUM CUSTOM EMOJI & 3D ASSETS ENGINE
 * =========================================================================
 * 
 * 📌 QAYSI QATORDA QAYSI EMOJI ID-SINI QO'YISH KERAK (O'ZINGIZ UCHUN ANIQ QO'LLANMA):
 * 
 * 30-qator: ⭐ Stars (Yulduzcha) 4988289890769699938
 * 33-qator: ⭐️ 1 Oylik Telegram Premium 5271998448042785916
 * 34-qator: ⚡️ 3 Oylik Telegram Premium 5271998448042785916
 * 35-qator: 💎 6 Oylik Telegram Premium 5271998448042785916
 * 36-qator: 👑 1 Yillik Telegram Premium 5271998448042785916
 * 
 * 39-qator: 🧸 1. Ayiqcha (Teddy Bear) sovg'a emoji 
 * 40-qator: 💖 2. Yurakcha (Heart) sovg'a emoji ID
 * 41-qator: 🌹 3. Qizil Atirgul (Rose) sovg'a emoji ID
 * 42-qator: 🎁 4. Syurpriz quti (Gift Box) sovg'a emoji ID
 * 43-qator: 💐 5. Lola guldastasi (Tulips) sovg'a emoji ID
 * 44-qator: 🚀 6. Kosmik Raketa (Rocket) sovg'a emoji ID
 * 45-qator: 🎂 7. Tug'ilgan kun torti (Cake) sovg'a emoji ID
 * 46-qator: 🍾 8. Shampan vinosi (Champagne) sovg'a emoji ID
 * 47-qator: 🏆 9. Oltin Kubok (Trophy) sovg'a emoji ID
 * 48-qator: 💎 10. Moviy Olmos (Diamond) sovg'a emoji ID
 * 49-qator: 💍 11. Brilliant Uzuk (Ring) sovg'a emoji ID
 * =========================================================================
 */

export const PREMIUM_EMOJI_IDS = {
  // ⭐ Stars:
  STAR: '5269623953898357794',            // 30-qator: Stars emoji ID

  // 💎 Telegram Premium Obunalari (1, 3, 6, 12 oylik):
  PREMIUM_1M: '5461082978794880873',      // 33-qator: 1 Oylik Telegram Premium emoji ID
  PREMIUM_3M: '5461082978794880873',      // 34-qator: 3 Oylik Telegram Premium emoji ID
  PREMIUM_6M: '5461082978794880873',      // 35-qator: 6 Oylik Telegram Premium emoji ID
  PREMIUM_12M: '5461082978794880873',     // 36-qator: 1 Yillik (12 oy) Telegram Premium emoji ID

  // 🎁 Telegram Rasmiy Sovg'alari (Image 1 dagi 11 ta gift):
  TEDDY: '5823511762548301106',          // 39-qator: Ayiqcha (Teddy Bear)
  HEART: '5823504508348537997',          // 40-qator: Yurakcha (Heart)
  ROSE: '5823675916198354199',           // 41-qator: Qizil Atirgul (Rose)
  GIFT: '5825844101588720291',           // 42-qator: Syurpriz quti (Gift Box)
  TULIPS: '5823675916198354199',         // 43-qator: Lola guldastasi (Tulips)
  ROCKET: '5825442788434517646',         // 44-qator: Kosmik Raketa (Rocket)
  CAKE: '5825603677909424544',           // 45-qator: Tug'ilgan kun torti (Cake)
  CHAMPAGNE: '5823279086990006647',      // 46-qator: Shampan vinosi (Champagne)
  TROPHY: '5823653586663382347',         // 47-qator: Oltin Kubok (Trophy)
  DIAMOND: '5823337017508895058',        // 48-qator: Moviy Olmos (Diamond)
  RING: '5823622048718527510'            // 49-qator: Brilliant Uzuk (Ring)
};

// Global oynaga ham bog'lab qo'yamiz (agar brauzer bo'lsa)
if (typeof window !== 'undefined') {
  window.PREMIUM_EMOJI_IDS = PREMIUM_EMOJI_IDS;
}

// LocalStorage dan foydalanuvchi o'zgartirgan bo'lsa o'qish
if (typeof localStorage !== 'undefined') {
  try {
    const saved = localStorage.getItem('sb_premium_emoji_ids');
    if (saved) {
      Object.assign(PREMIUM_EMOJI_IDS, JSON.parse(saved));
    }
  } catch (e) { }
}

// =========================================================================
// 3D ANIMATED VECTOR GRAPHICS GENERATOR (Real Telegram App Style)
// =========================================================================

/**
 * Helper to wrap icons with Telegram <tg-emoji> tag and custom emoji 180-frame Lottie animation with SVG fallback
 */
export function wrapWithTgEmojiAndFallback(customId, fallbackSvg, size = 34) {
  if (!customId) return fallbackSvg;
  return `<tg-emoji emoji-id="${customId}" class="tg-emoji-lottie-wrap" style="display:inline-flex;align-items:center;justify-content:center;width:${size}px;height:${size}px;position:relative;vertical-align:middle;overflow:visible;">
    <div class="tg-lottie-anim" data-emoji-id="${customId}" style="width:${size}px;height:${size}px;position:absolute;top:0;left:0;display:none;pointer-events:none;z-index:2;"></div>
    <div class="tg-emoji-static-fallback" style="width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center;position:relative;z-index:1;">
      ${fallbackSvg}
    </div>
  </tg-emoji>`;
}

const emojiLottieDataCache = new Map();
const pendingEmojiFetches = new Map();

export async function fetchEmojiAnimationData(emojiId) {
  if (emojiLottieDataCache.has(emojiId)) {
    return emojiLottieDataCache.get(emojiId);
  }
  if (pendingEmojiFetches.has(emojiId)) {
    return pendingEmojiFetches.get(emojiId);
  }

  const fetchPromise = (async () => {
    try {
      const resp = await fetch(`/api/emoji-animation?id=${emojiId}`);
      if (!resp.ok) return null;
      const ct = resp.headers.get('content-type') || '';
      if (ct.includes('json')) {
        const json = await resp.json();
        const item = { type: 'json', data: json };
        emojiLottieDataCache.set(emojiId, item);
        return item;
      } else if (ct.includes('video') || ct.includes('webm')) {
        const item = { type: 'video', url: `/api/emoji-animation?id=${emojiId}` };
        emojiLottieDataCache.set(emojiId, item);
        return item;
      }
      return null;
    } catch (err) {
      console.warn('Emoji animation fetch failed for:', emojiId, err);
      return null;
    } finally {
      pendingEmojiFetches.delete(emojiId);
    }
  })();

  pendingEmojiFetches.set(emojiId, fetchPromise);
  return fetchPromise;
}

export function initAllLottieAnimations(root = document) {
  if (typeof window === 'undefined') return;

  const elements = root.querySelectorAll('.tg-lottie-anim[data-emoji-id]:not([data-loaded="true"])');
  if (!elements || elements.length === 0) return;

  elements.forEach(async (el) => {
    if (el.getAttribute('data-loaded') === 'true' || el.getAttribute('data-loading') === 'true') {
      return;
    }
    el.setAttribute('data-loading', 'true');
    const emojiId = el.getAttribute('data-emoji-id');
    if (!emojiId) return;

    try {
      const animInfo = await fetchEmojiAnimationData(emojiId);
      if (!animInfo) {
        el.removeAttribute('data-loading');
        return;
      }

      if (animInfo.type === 'json' && window.lottie) {
        // Deep copy data so lottie doesn't mutate it
        const cloned = JSON.parse(JSON.stringify(animInfo.data));
        el.innerHTML = '';
        const anim = window.lottie.loadAnimation({
          container: el,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          animationData: cloned,
          rendererSettings: {
            preserveAspectRatio: 'xMidYMid meet',
            clearCanvas: false
          }
        });

        const showLive = () => {
          el.style.display = 'block';
          const fallback = el.parentElement?.querySelector('.tg-emoji-static-fallback');
          if (fallback) fallback.style.display = 'none';
        };

        anim.addEventListener('DOMLoaded', showLive);
        showLive();

        el.setAttribute('data-loaded', 'true');
        el.removeAttribute('data-loading');
      } else if (animInfo.type === 'video') {
        el.innerHTML = `<video src="${animInfo.url}" autoplay loop muted playsinline style="width:100%;height:100%;object-fit:contain;pointer-events:none;"></video>`;
        el.style.display = 'block';
        const fallback = el.parentElement?.querySelector('.tg-emoji-static-fallback');
        if (fallback) fallback.style.display = 'none';
        el.setAttribute('data-loaded', 'true');
        el.removeAttribute('data-loading');
      }
    } catch (e) {
      console.warn('Could not load Lottie animation for', emojiId, e);
      el.removeAttribute('data-loading');
    }
  });
}

if (typeof window !== 'undefined') {
  window.initAllLottieAnimations = initAllLottieAnimations;
}

/**
 * 1. Faceted 3D Telegram Star SVG (Vibrant Gold Glowing Star)
 */
export function getTelegramStarSvg(size = 28, extraClass = 'tg-3d-star anim-float') {
  const customId = PREMIUM_EMOJI_IDS.STAR;
  const uid = 'star_' + Math.floor(Math.random() * 100000);
  const svg = `
    <svg class="${extraClass}" width="${size}" height="${size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="sg_${uid}" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#FFE769" stop-opacity="0.7"/>
          <stop offset="100%" stop-color="#FF9900" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="ft_${uid}" x1="50" y1="6" x2="50" y2="52" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FFFBE6"/>
          <stop offset="35%" stop-color="#FFDE59"/>
          <stop offset="100%" stop-color="#FFA800"/>
        </linearGradient>
        <linearGradient id="fl_${uid}" x1="6" y1="36" x2="50" y2="52" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FFB300"/>
          <stop offset="100%" stop-color="#E66700"/>
        </linearGradient>
        <linearGradient id="fr_${uid}" x1="94" y1="36" x2="50" y2="52" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FFA000"/>
          <stop offset="100%" stop-color="#CC4E00"/>
        </linearGradient>
        <linearGradient id="fbl_${uid}" x1="22" y1="92" x2="50" y2="52" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FFA800"/>
          <stop offset="100%" stop-color="#A83800"/>
        </linearGradient>
        <linearGradient id="fbr_${uid}" x1="78" y1="92" x2="50" y2="52" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#E65C00"/>
          <stop offset="100%" stop-color="#7A2200"/>
        </linearGradient>
        <linearGradient id="glint_${uid}" x1="42" y1="10" x2="56" y2="45" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
          <stop offset="60%" stop-color="#FFFFFF" stop-opacity="0.15"/>
          <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="46" fill="url(#sg_${uid})"/>
      <path d="M50 6 L63 36 L50 52 L37 36 Z" fill="url(#ft_${uid})" stroke="#FFE27A" stroke-width="0.75"/>
      <path d="M94 36 L70 64 L50 52 L63 36 Z" fill="url(#fr_${uid})" stroke="#FF9900" stroke-width="0.75"/>
      <path d="M78 92 L50 72 L50 52 L70 64 Z" fill="url(#fbr_${uid})" stroke="#B84000" stroke-width="0.75"/>
      <path d="M22 92 L30 64 L50 52 L50 72 Z" fill="url(#fbl_${uid})" stroke="#A83800" stroke-width="0.75"/>
      <path d="M6 36 L37 36 L50 52 L30 64 Z" fill="url(#fl_${uid})" stroke="#FFB000" stroke-width="0.75"/>
      <path d="M50 9 L58 35 L50 48 L42 35 Z" fill="url(#glint_${uid})"/>
      <circle cx="50" cy="22" r="2" fill="#FFFFFF" opacity="0.85"/>
    </svg>
  `;
  return wrapWithTgEmojiAndFallback(customId, svg, size);
}

/**
 * 2. 3D Telegram Premium Subscriptions Badges (1, 3, 6, 12 oylik) - Official Telegram Premium Star
 */
export function getTelegramPremiumBadgeSvg(duration = 1, size = 34) {
  const uid = 'pm_' + Math.floor(Math.random() * 100000);
  let customId = PREMIUM_EMOJI_IDS.PREMIUM_1M;
  if (duration === 3) customId = PREMIUM_EMOJI_IDS.PREMIUM_3M;
  else if (duration === 6) customId = PREMIUM_EMOJI_IDS.PREMIUM_6M;
  else if (duration === 12) customId = PREMIUM_EMOJI_IDS.PREMIUM_12M;

  // Official Telegram Premium purple/magenta gradient for all durations
  const colorStart = '#E9D5FF';
  const colorMid = '#A855F7';
  const colorEnd = '#7E22CE';
  const glowColor = '#C084FC';
  const strokeColor = '#F472B6';

  // Official Telegram 8-Pointed Premium Star Vector with Facets and Glint
  const svgBody = `
    <defs>
      <radialGradient id="pmg_${uid}" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="${glowColor}" stop-opacity="0.75"/>
        <stop offset="60%" stop-color="${glowColor}" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="${glowColor}" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="pms_${uid}" x1="20" y1="10" x2="80" y2="90" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="${colorStart}"/>
        <stop offset="50%" stop-color="${colorMid}"/>
        <stop offset="100%" stop-color="${colorEnd}"/>
      </linearGradient>
      <linearGradient id="pm_facet_top_${uid}" x1="50" y1="6" x2="50" y2="50" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.1"/>
      </linearGradient>
    </defs>
    <!-- Soft Glow Backdrop -->
    <circle cx="50" cy="50" r="46" fill="url(#pmg_${uid})"/>
    
    <!-- 8-Pointed Telegram Premium Star Base -->
    <path d="M50 6 L58 32 L78 22 L68 42 L94 50 L68 58 L78 78 L58 68 L50 94 L42 68 L22 78 L32 58 L6 50 L32 42 L22 22 L42 32 Z" 
          fill="url(#pms_${uid})" stroke="${strokeColor}" stroke-width="1.2" stroke-linejoin="round"/>
          
    <!-- 3D Facets (Top Point Light) -->
    <polygon points="50,6 58,32 50,50" fill="url(#pm_facet_top_${uid})"/>
    <polygon points="50,6 42,32 50,50" fill="#FFFFFF" fill-opacity="0.3"/>
    
    <!-- 3D Facets (Right & Left Highlights) -->
    <polygon points="94,50 68,42 50,50" fill="#FFFFFF" fill-opacity="0.35"/>
    <polygon points="6,50 32,42 50,50" fill="#FFFFFF" fill-opacity="0.4"/>
    
    <!-- Center Sparkling Starburst Glint -->
    <polygon points="50,36 53,47 64,50 53,53 50,64 47,53 36,50 47,47" fill="#FFFFFF"/>
    <circle cx="50" cy="50" r="2.5" fill="#FFFFFF"/>
    <circle cx="50" cy="18" r="1.5" fill="#FFFFFF" opacity="0.9"/>
  `;

  const svg = `
    <svg class="tg-prem-badge-svg anim-float" width="${size}" height="${size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      ${svgBody}
    </svg>
  `;
  return wrapWithTgEmojiAndFallback(customId, svg, size);
}

/**
 * 3. 3D Telegram Gifts Illustrations Generator (11 Real Gifts matching Image 1)
 */
export function getGift3DIconSvg(giftId, size = 56) {
  const uid = 'g_' + giftId + '_' + Math.floor(Math.random() * 100000);
  let emojiId = PREMIUM_EMOJI_IDS.TEDDY;
  let svgContent = '';

  switch (giftId) {
    case 'teddy':
      emojiId = PREMIUM_EMOJI_IDS.TEDDY;
      // 1. 3D Teddy Bear with soft brown shading, snout, and shiny eyes
      svgContent = `
        <defs>
          <radialGradient id="tbg_${uid}" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stop-color="#E0A96D"/>
            <stop offset="60%" stop-color="#C28243"/>
            <stop offset="100%" stop-color="#8F531B"/>
          </radialGradient>
          <radialGradient id="tbe_${uid}" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stop-color="#FCE1C2"/>
            <stop offset="100%" stop-color="#D49959"/>
          </radialGradient>
        </defs>
        <!-- Ears -->
        <circle cx="30" cy="28" r="13" fill="url(#tbg_${uid})"/>
        <circle cx="30" cy="28" r="8" fill="url(#tbe_${uid})"/>
        <circle cx="70" cy="28" r="13" fill="url(#tbg_${uid})"/>
        <circle cx="70" cy="28" r="8" fill="url(#tbe_${uid})"/>
        <!-- Body & Arms -->
        <ellipse cx="50" cy="68" rx="28" ry="24" fill="url(#tbg_${uid})"/>
        <ellipse cx="22" cy="64" rx="10" ry="14" fill="url(#tbg_${uid})" transform="rotate(20 22 64)"/>
        <ellipse cx="78" cy="64" rx="10" ry="14" fill="url(#tbg_${uid})" transform="rotate(-20 78 64)"/>
        <!-- Paws -->
        <circle cx="34" cy="85" r="9" fill="url(#tbe_${uid})"/>
        <circle cx="66" cy="85" r="9" fill="url(#tbe_${uid})"/>
        <!-- Head -->
        <circle cx="50" cy="42" r="24" fill="url(#tbg_${uid})"/>
        <!-- Snout -->
        <ellipse cx="50" cy="48" rx="12" ry="9" fill="url(#tbe_${uid})"/>
        <ellipse cx="50" cy="44" rx="5" ry="3.5" fill="#3D1E08"/>
        <!-- Eyes with shine -->
        <circle cx="41" cy="38" r="3.2" fill="#241306"/>
        <circle cx="42" cy="37" r="1" fill="#FFFFFF"/>
        <circle cx="59" cy="38" r="3.2" fill="#241306"/>
        <circle cx="60" cy="37" r="1" fill="#FFFFFF"/>
      `;
      break;

    case 'heart':
      emojiId = PREMIUM_EMOJI_IDS.HEART;
      // 2. 3D Glossy Pink Heart with Golden Silk Ribbon Bow
      svgContent = `
        <defs>
          <linearGradient id="hg_${uid}" x1="20" y1="15" x2="80" y2="85" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FF70A6"/>
            <stop offset="45%" stop-color="#FF2A7A"/>
            <stop offset="100%" stop-color="#BA0B4B"/>
          </linearGradient>
          <linearGradient id="rb_${uid}" x1="20" y1="35" x2="80" y2="65" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFF385"/>
            <stop offset="50%" stop-color="#FFD700"/>
            <stop offset="100%" stop-color="#E69500"/>
          </linearGradient>
          <filter id="hsh_${uid}"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#FF2A7A" flood-opacity="0.5"/></filter>
        </defs>
        <!-- Heart Path -->
        <path d="M50 84 C25 68 12 50 12 34 C12 18 25 12 36 12 C44 12 48 18 50 22 C52 18 56 12 64 12 C75 12 88 18 88 34 C88 50 75 68 50 84 Z" 
              fill="url(#hg_${uid})" filter="url(#hsh_${uid})"/>
        <!-- Highlight -->
        <ellipse cx="32" cy="24" rx="10" ry="5" fill="#FFF" opacity="0.45" transform="rotate(-30 32 24)"/>
        <!-- Ribbon Wrap -->
        <path d="M18 42 Q50 56 82 42 L80 49 Q50 63 20 49 Z" fill="url(#rb_${uid})" stroke="#FFF" stroke-width="0.5"/>
        <!-- Bow in center -->
        <circle cx="50" cy="51" r="5" fill="url(#rb_${uid})" stroke="#FFE600" stroke-width="0.8"/>
        <path d="M50 51 C40 38 28 45 45 52 Z" fill="url(#rb_${uid})"/>
        <path d="M50 51 C60 38 72 45 55 52 Z" fill="url(#rb_${uid})"/>
        <path d="M50 54 Q40 68 36 74 L42 74 Q50 60 52 54 Z" fill="url(#rb_${uid})"/>
        <path d="M50 54 Q60 68 64 74 L58 74 Q50 60 48 54 Z" fill="url(#rb_${uid})"/>
      `;
      break;

    case 'rose':
      emojiId = PREMIUM_EMOJI_IDS.ROSE;
      // 3. 3D Velvet Red Rose on Green Stem with Leaves
      svgContent = `
        <defs>
          <linearGradient id="rg_${uid}" x1="30" y1="15" x2="70" y2="65" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FF4D6D"/>
            <stop offset="40%" stop-color="#C9184A"/>
            <stop offset="100%" stop-color="#590D22"/>
          </linearGradient>
          <linearGradient id="st_${uid}" x1="50" y1="50" x2="50" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#40916C"/>
            <stop offset="100%" stop-color="#1B4332"/>
          </linearGradient>
        </defs>
        <!-- Stem & Leaves -->
        <path d="M50 50 Q52 70 48 90" stroke="url(#st_${uid})" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M50 65 Q68 60 74 68 Q65 76 50 67 Z" fill="#2D6A4F"/>
        <path d="M49 73 Q32 70 26 78 Q36 84 49 75 Z" fill="#2D6A4F"/>
        <!-- Rose Petals -->
        <circle cx="50" cy="36" r="22" fill="url(#rg_${uid})"/>
        <path d="M34 26 C36 16 52 14 62 20 C68 28 66 38 60 44 C48 54 36 44 34 26 Z" fill="#A4133C"/>
        <path d="M40 28 C42 20 54 20 58 26 C60 34 52 38 48 38 C42 38 38 34 40 28 Z" fill="#FF4D6D"/>
        <path d="M46 30 C48 24 54 24 55 28 C56 32 50 34 48 34 Z" fill="#FFF0F3" opacity="0.8"/>
      `;
      break;

    case 'surprise':
    case 'gift':
      emojiId = PREMIUM_EMOJI_IDS.GIFT;
      // 4. Green Surprise Gift Box with Floating Gold Stars & Confetti
      svgContent = `
        <defs>
          <linearGradient id="bg_${uid}" x1="20" y1="40" x2="80" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#34D399"/>
            <stop offset="50%" stop-color="#059669"/>
            <stop offset="100%" stop-color="#064E3B"/>
          </linearGradient>
          <linearGradient id="yg_${uid}" x1="30" y1="10" x2="70" y2="50" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFF566"/>
            <stop offset="100%" stop-color="#F59E0B"/>
          </linearGradient>
        </defs>
        <!-- Floating Yellow Stars & Confetti from Box -->
        <polygon points="50,10 53,19 62,20 55,26 57,35 50,30 43,35 45,26 38,20 47,19" fill="url(#yg_${uid})"/>
        <circle cx="32" cy="18" r="2.5" fill="#38BDF8"/>
        <circle cx="68" cy="16" r="2.5" fill="#F43F5E"/>
        <circle cx="76" cy="28" r="2" fill="#FBBF24"/>
        <circle cx="24" cy="28" r="2" fill="#A855F7"/>
        <!-- Box Base -->
        <rect x="24" y="48" width="52" height="38" rx="6" fill="url(#bg_${uid})"/>
        <rect x="46" y="48" width="8" height="38" fill="url(#yg_${uid})"/>
        <!-- Open Lid Tilted -->
        <rect x="18" y="40" width="64" height="12" rx="4" fill="#10B981" stroke="#34D399" stroke-width="0.8"/>
        <rect x="46" y="40" width="8" height="12" fill="url(#yg_${uid})"/>
        <ellipse cx="50" cy="40" rx="6" ry="3" fill="#F59E0B"/>
      `;
      break;

    case 'tulips':
      emojiId = PREMIUM_EMOJI_IDS.TULIPS;
      // 5. Bouquet of Vibrant Tulips with lush leaves
      svgContent = `
        <defs>
          <linearGradient id="yl_${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FDE047"/><stop offset="100%" stop-color="#EAB308"/></linearGradient>
          <linearGradient id="rd_${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FB7185"/><stop offset="100%" stop-color="#E11D48"/></linearGradient>
          <linearGradient id="pr_${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#C084FC"/><stop offset="100%" stop-color="#9333EA"/></linearGradient>
        </defs>
        <!-- Stems tied together -->
        <path d="M48 50 L42 88" stroke="#15803D" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M50 50 L50 88" stroke="#16A34A" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M52 50 L58 88" stroke="#15803D" stroke-width="3.5" stroke-linecap="round"/>
        <!-- Leaves -->
        <path d="M40 70 Q24 55 30 40 Q44 55 42 70 Z" fill="#22C55E"/>
        <path d="M60 70 Q76 55 70 40 Q56 55 58 70 Z" fill="#22C55E"/>
        <!-- Tulips -->
        <!-- Center Yellow Tulip -->
        <path d="M40 38 C40 22 50 18 50 18 C50 18 60 22 60 38 C60 48 40 48 40 38 Z" fill="url(#yl_${uid})"/>
        <!-- Left Red Tulip -->
        <path d="M26 44 C24 30 35 24 35 24 C35 24 45 28 43 44 C40 52 26 52 26 44 Z" fill="url(#rd_${uid})" transform="rotate(-15 35 38)"/>
        <!-- Right Purple Tulip -->
        <path d="M58 44 C56 28 66 24 66 24 C66 24 76 30 74 44 C72 52 58 52 58 44 Z" fill="url(#pr_${uid})" transform="rotate(15 65 38)"/>
      `;
      break;

    case 'rocket':
      emojiId = PREMIUM_EMOJI_IDS.ROCKET;
      // 6. Sleek Space Rocket with Fire Exhaust Blasting Diagonally
      svgContent = `
        <defs>
          <linearGradient id="rk_${uid}" x1="30" y1="20" x2="70" y2="60" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFFFFF"/><stop offset="50%" stop-color="#E2E8F0"/><stop offset="100%" stop-color="#94A3B8"/>
          </linearGradient>
          <linearGradient id="fr_${uid}" x1="50" y1="60" x2="50" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FDE047"/><stop offset="50%" stop-color="#F97316"/><stop offset="100%" stop-color="#EF4444"/>
          </linearGradient>
        </defs>
        <!-- Fire Exhaust -->
        <path d="M44 68 Q50 92 50 92 Q50 92 56 68 Z" fill="url(#fr_${uid})" transform="rotate(45 50 50)"/>
        <path d="M47 68 Q50 82 50 82 Q50 82 53 68 Z" fill="#FFF" transform="rotate(45 50 50)"/>
        <!-- Rocket Body tilted -->
        <g transform="rotate(45 50 50)">
          <!-- Fins -->
          <polygon points="34,54 24,70 38,66" fill="#EF4444"/>
          <polygon points="66,54 76,70 62,66" fill="#EF4444"/>
          <!-- Body -->
          <ellipse cx="50" cy="46" rx="15" ry="26" fill="url(#rk_${uid})"/>
          <!-- Nosecone -->
          <path d="M35 34 Q50 14 50 14 Q50 14 65 34 Z" fill="#EF4444"/>
          <!-- Porthole window -->
          <circle cx="50" cy="42" r="6" fill="#38BDF8" stroke="#0284C7" stroke-width="1.5"/>
          <circle cx="48" cy="40" r="1.8" fill="#FFF"/>
        </g>
      `;
      break;

    case 'cake':
      emojiId = PREMIUM_EMOJI_IDS.CAKE;
      // 7. White Frosted Birthday Cake with Red Cherries & 4 Lit Candles
      svgContent = `
        <defs>
          <linearGradient id="ck_${uid}" x1="20" y1="40" x2="80" y2="80" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFFFFF"/><stop offset="70%" stop-color="#F1F5F9"/><stop offset="100%" stop-color="#CBD5E1"/>
          </linearGradient>
          <linearGradient id="flm_${uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FDE047"/><stop offset="100%" stop-color="#EA580C"/></linearGradient>
        </defs>
        <!-- Cake Base Cylinder -->
        <ellipse cx="50" cy="74" rx="34" ry="12" fill="#E2E8F0"/>
        <rect x="16" y="52" width="68" height="22" fill="url(#ck_${uid})"/>
        <ellipse cx="50" cy="52" rx="34" ry="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="0.75"/>
        <!-- Chocolate / Strawberry Drips -->
        <path d="M16 54 Q24 64 32 54 Q40 66 50 54 Q60 66 68 54 Q76 64 84 54" stroke="#F43F5E" stroke-width="3" fill="none" stroke-linecap="round"/>
        <!-- Cherries -->
        <circle cx="28" cy="50" r="3.5" fill="#DC2626"/>
        <circle cx="50" cy="52" r="3.5" fill="#DC2626"/>
        <circle cx="72" cy="50" r="3.5" fill="#DC2626"/>
        <!-- 4 Candles & Flames -->
        <!-- Candle 1 -->
        <rect x="30" y="34" width="3" height="14" rx="1.5" fill="#38BDF8"/>
        <ellipse cx="31.5" cy="28" rx="2" ry="4" fill="url(#flm_${uid})"/>
        <!-- Candle 2 -->
        <rect x="43" y="32" width="3" height="15" rx="1.5" fill="#F472B6"/>
        <ellipse cx="44.5" cy="26" rx="2" ry="4" fill="url(#flm_${uid})"/>
        <!-- Candle 3 -->
        <rect x="55" y="32" width="3" height="15" rx="1.5" fill="#FBBF24"/>
        <ellipse cx="56.5" cy="26" rx="2" ry="4" fill="url(#flm_${uid})"/>
        <!-- Candle 4 -->
        <rect x="67" y="34" width="3" height="14" rx="1.5" fill="#34D399"/>
        <ellipse cx="68.5" cy="28" rx="2" ry="4" fill="url(#flm_${uid})"/>
      `;
      break;

    case 'champagne':
      emojiId = PREMIUM_EMOJI_IDS.CHAMPAGNE;
      // 8. Dark Green Champagne Bottle with Gold Foil Neck & Popped Cork
      svgContent = `
        <defs>
          <linearGradient id="chg_${uid}" x1="30" y1="30" x2="70" y2="70" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#14532D"/><stop offset="50%" stop-color="#052E16"/><stop offset="100%" stop-color="#021E0E"/>
          </linearGradient>
          <linearGradient id="gld_${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FDE047"/><stop offset="100%" stop-color="#B45309"/></linearGradient>
        </defs>
        <!-- Bubbles shooting out -->
        <circle cx="68" cy="18" r="3" fill="#FDE047" opacity="0.8"/>
        <circle cx="76" cy="12" r="2.2" fill="#FDE047" opacity="0.7"/>
        <circle cx="82" cy="20" r="1.8" fill="#FDE047" opacity="0.6"/>
        <!-- Cork popped -->
        <rect x="66" y="24" width="6" height="8" rx="2" fill="#D97706" transform="rotate(35 69 28)"/>
        <!-- Bottle tilted -->
        <g transform="rotate(-35 50 50)">
          <!-- Body -->
          <rect x="40" y="44" width="20" height="38" rx="4" fill="url(#chg_${uid})"/>
          <!-- Shoulders & Neck -->
          <path d="M40 44 Q50 34 46 22 L54 22 Q50 34 60 44 Z" fill="url(#chg_${uid})"/>
          <!-- Gold Neck Foil -->
          <rect x="46" y="20" width="8" height="12" rx="1" fill="url(#gld_${uid})"/>
          <!-- Label on Bottle -->
          <rect x="42" y="52" width="16" height="18" rx="2" fill="#FFFBEB" stroke="#B45309" stroke-width="0.6"/>
        </g>
      `;
      break;

    case 'trophy':
      emojiId = PREMIUM_EMOJI_IDS.TROPHY;
      // 9. Gleaming Gold Trophy Cup on Wooden Stand with Handles
      svgContent = `
        <defs>
          <linearGradient id="trg_${uid}" x1="20" y1="15" x2="80" y2="65" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFFBEB"/>
            <stop offset="35%" stop-color="#FBBF24"/>
            <stop offset="80%" stop-color="#D97706"/>
            <stop offset="100%" stop-color="#78350F"/>
          </linearGradient>
        </defs>
        <!-- Base Stand -->
        <rect x="36" y="78" width="28" height="10" rx="2" fill="#451A03" stroke="#78350F" stroke-width="1"/>
        <rect x="44" y="68" width="12" height="11" fill="url(#trg_${uid})"/>
        <!-- Trophy Handles -->
        <path d="M30 26 C16 26 18 48 34 48" stroke="url(#trg_${uid})" stroke-width="4.5" fill="none" stroke-linecap="round"/>
        <path d="M70 26 C84 26 82 48 66 48" stroke="url(#trg_${uid})" stroke-width="4.5" fill="none" stroke-linecap="round"/>
        <!-- Main Cup -->
        <path d="M28 20 L72 20 Q70 54 50 64 Q30 54 28 20 Z" fill="url(#trg_${uid})" stroke="#FDE047" stroke-width="1"/>
        <ellipse cx="50" cy="20" rx="22" ry="5" fill="#FEF08A"/>
        <circle cx="50" cy="38" r="6" fill="#FDE047" opacity="0.6"/>
      `;
      break;

    case 'diamond':
      emojiId = PREMIUM_EMOJI_IDS.DIAMOND;
      // 10. Multifaceted Sky Blue Gemstone Diamond with Specular Shine
      svgContent = `
        <defs>
          <linearGradient id="dmg_${uid}" x1="20" y1="20" x2="80" y2="80" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#E0F2FE"/>
            <stop offset="40%" stop-color="#38BDF8"/>
            <stop offset="100%" stop-color="#0369A1"/>
          </linearGradient>
        </defs>
        <polygon points="30,22 70,22 88,44 12,44" fill="#7DD3FC" stroke="#E0F2FE" stroke-width="1"/>
        <polygon points="12,44 50,86 36,44" fill="#0284C7" stroke="#38BDF8" stroke-width="1"/>
        <polygon points="88,44 50,86 64,44" fill="#0369A1" stroke="#38BDF8" stroke-width="1"/>
        <polygon points="36,44 50,86 64,44" fill="#38BDF8" stroke="#E0F2FE" stroke-width="1"/>
        <polygon points="40,22 60,22 64,44 36,44" fill="#BAE6FD"/>
        <!-- Sparkle starburst -->
        <circle cx="32" cy="30" r="2" fill="#FFF"/>
        <path d="M72 32 L75 36 L72 40 L69 36 Z" fill="#FFF"/>
      `;
      break;

    case 'ring':
      emojiId = PREMIUM_EMOJI_IDS.RING;
      // 11. Silver Platinum Band with Giant Sparkling Solitaire Diamond
      svgContent = `
        <defs>
          <linearGradient id="rng_${uid}" x1="20" y1="35" x2="80" y2="85" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#FFFFFF"/><stop offset="50%" stop-color="#CBD5E1"/><stop offset="100%" stop-color="#64748B"/>
          </linearGradient>
        </defs>
        <!-- Platinum Ring Loop -->
        <circle cx="50" cy="58" r="26" stroke="url(#rng_${uid})" stroke-width="7" fill="none"/>
        <circle cx="50" cy="58" r="26" stroke="#FFFFFF" stroke-width="1.5" fill="none" opacity="0.6"/>
        <!-- Ring Mount Prongs -->
        <path d="M43 36 L50 30 L57 36" stroke="#94A3B8" stroke-width="3" fill="none"/>
        <!-- Giant Solitaire Diamond -->
        <polygon points="41,20 59,20 66,28 34,28" fill="#E0F2FE" stroke="#FFF" stroke-width="0.8"/>
        <polygon points="34,28 50,42 66,28" fill="#38BDF8" stroke="#7DD3FC" stroke-width="0.8"/>
        <polygon points="42,28 50,42 58,28" fill="#BAE6FD"/>
        <!-- Diamond Glisten Sparkle -->
        <circle cx="50" cy="24" r="2.5" fill="#FFF"/>
        <polygon points="62,14 64,18 68,20 64,22 62,26 60,22 56,20 60,18" fill="#FFF"/>
      `;
      break;

    default:
      emojiId = PREMIUM_EMOJI_IDS.GIFT;
      svgContent = `<circle cx="50" cy="50" r="30" fill="#F5BA22"/>`;
  }

  const fullSvg = `
    <svg class="gift-icon-preview anim-float" width="${size}" height="${size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      ${svgContent}
    </svg>
  `;
  return wrapWithTgEmojiAndFallback(emojiId, fullSvg, size);
}
