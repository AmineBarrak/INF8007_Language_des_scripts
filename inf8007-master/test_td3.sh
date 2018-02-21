#!/usr/bin/env bash
res=`mktemp`
expected='03/expected'
curl -s 'http://localhost:8765/?acronym=INF8007' > $res
test "$?" -eq 7 && echo "Verifiez que le serveur est prêt à recevoir des requetes" && exit 1
diff $expected $res
rm $res
exit $?