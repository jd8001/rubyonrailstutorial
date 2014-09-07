MySQL Command used for stock selection:

use stocks; select ticker, rank, price, reteq, earnyield from current where cap>2000000 and earnyield<.4 and reteq<.4 and price>3 order by rank desc limit 20;

Use your thinking cap, research the stocks and only pick something that makes sense to you. 