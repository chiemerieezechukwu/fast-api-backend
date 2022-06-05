#!/bin/bash
set -xe

domain_prefix=$1
authorization_code=$2
client_id=$3
region=eu-central-1

curl --location --request POST "https://$domain_prefix.auth.$region.amazoncognito.com/oauth2/token" \
--header "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "client_id=$client_id" \
--data-urlencode "code=$authorization_code" \
--data-urlencode "grant_type=authorization_code" \
--data-urlencode "redirect_uri=http://localhost" | jq
