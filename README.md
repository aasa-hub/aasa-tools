# aasa-tools

Working repo for AASA on-chain tooling. First entry: a public verifier for the FLAPJAX token, its treasury and its two PancakeSwap V3 pools on BNB Smart Chain.

Live: https://aasa-hub.github.io/aasa-tools/

## flapjax verifier

Open the Pages URL (or `index.html` locally) and the page reads everything live from a public BSC RPC at one pinned block: `eth_blockNumber` first, then every `eth_call`, `eth_getCode` and `eth_getStorageAt` pinned to that block. Nothing is precomputed, there is no backend, no API key and no tracking.

Checks:

- the token address has runtime code at the pinned block
- `symbol()` is FLAPJAX, `decimals()` is 18, `totalSupply()` reported as-is with no price attached
- `owner()` is the zero address
- the EIP-1967 implementation and admin storage slots are both zero, so it is not a proxy
- sixteen privileged selectors (`mint`, `pause`, `blacklist`, `setTax`, `setFee`, `excludeFromFee`, `upgradeTo`, ...) are searched for inside the deployed runtime bytecode
- the treasury's FLAPJAX balance via `balanceOf`
- both pools: token ordering, fee tier, `liquidity()` and `slot0().sqrtPriceX96`

Not measured, stated rather than guessed: LP lock ownership (that needs the locker contract's own state), holder distribution, and off-chain claim review.

## reference run

Block 132329972 on `bsc-rpc.publicnode.com`: 2,901 bytes of token runtime code, FLAPJAX with 18 decimals, supply 44,444,444,444, owner zero, both proxy slots zero, none of the sixteen privileged selectors, treasury 825,796,348 FJ, primary FLAPJAX/WBNB pool liquidity 320,678,316,678,999,036,604,866, secondary FLAPJAX/BTCB pool liquidity 0.

## addresses

- token `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df`
- treasury `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`
- FLAPJAX/WBNB 1% `0xca93ec685b8623688e6b236f9068034b298c2150`
- FLAPJAX/BTCB 1% `0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e`

## cli

`python3 verify.py` runs the same checks without a browser.

MIT. compute = calories.
