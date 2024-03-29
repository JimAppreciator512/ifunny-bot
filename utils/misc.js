export const avatarIcon =
    "https://imageproxy.ifunny.co/crop:square,resize:100x,quality:90/user_photos/57459299098918f644f560dc5e73e0c4a10c9495_0.webp";
export const iFunnyIcon =
    "https://play-lh.googleusercontent.com/Wr4GnjKU360bQEFoVimXfi-OlA6To9DkdrQBQ37CMdx1Kx5gRE07MgTDh1o7lAPV1ws";

export const footerQuotes = [
    { quote: "Go out and be based.", author: "anonymous" },
    {
        quote: "A based man in a cringe place makes all the difference.",
        author: "The G-Man",
    },
    {
        quote: "It's good to be king. Wait, maybe. I think maybe I'm just like a little bizarre little person who walks back and forth. Whatever, you know, but...",
        author: "Terry Davis",
    },
    {
        quote: "All my characters are me. I'm not a good enough actor to become a character. I hear about actors who become the role and I think 'I wonder what that feels like.' Because for me, they're all me.",
        author: "Ryan Gosling",
    },
    { quote: "I gotta fart", author: "me" },
    {
        quote: "Do not compare yourself to others. If you do so, you are insulting yourself.",
        author: "anonymous",
    },
    {
        quote: "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
        author: "John 3:16",
    },
    {
        quote: "Why should you feel anger at the world? As if the world would notice.",
        author: "Marcus Aurelius",
    },
    { quote: "What? Rappers say it all the time.", author: "Asuka Soryu" },
    { quote: "Wash your penis.", author: "Jorden Peterson" },
    { quote: "I am a federal agent.", author: "I'm being serious" },
    {
        quote: "Imagine being so universally despised that there has to be laws to prevent people from hating you.",
        author: "anonymous",
    },
    { quote: "He's literally me.", author: "Ryan Gosling" },
];

export function randomQuote() {
    // choosing the quote
    const quote = footerQuotes[Math.floor(Math.random() * footerQuotes.length)];

    // joining the fields
    return `"${quote.quote}" - ${quote.author}`;
}

// some handpicked posts
export function chooseRandomPost() {
    const posts = [
        "https://ifunny.co/gif/dwi-fondling-his-bulls-balls-as-he-does-his-wife-JOqBtxEfA",
        "https://ifunny.co/gif/me-after-i-host-funny-clash-2023-with-the-headlining-IK8N9RwhA",
        "https://ifunny.co/video/riggs-and-dwi-listing-out-the-age-range-they-ve-WebODXSjA",
        "https://ifunny.co/video/qN0jEBRCA",
        "https://ifunny.co/gif/deep-web-intel-zqBDS10aA",
        "https://ifunny.co/gif/deep-web-intel-when-you-mention-the-archive-link-or-exo1giA98",
        "https://ifunny.co/picture/deep-web-intel-vs-his-fat-gf-s-dad-2mBos8df8",
    ];

    return posts[Math.floor(Math.random() * posts.length)];
}

