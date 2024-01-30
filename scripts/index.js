const axios = require('axios');
const fs = require('fs');
const path = require('path');

const F5_NON_PROD = 'https://mod-ptc-nonprod.mdgapp.net';
const F5_PROD_PTC = 'https://mod-ptc-prod.mdgapp.net';
const F5_PROD_CTC = 'https://mod-ctc-prod.mdgapp.net';
const BACKUP_LOCATION = path.resolve('f5_config/');

/**
 * https://clouddocs.f5.com/api/icontrol-rest/APIRef_tm_ltm_data-group_internal.html
 */
async function datagroups(url, destination) {
    const res = await request(`${url}/mgmt/tm/ltm/data-group/internal`);

    if (res.status === 200) {
        const backupDir = path.join(BACKUP_LOCATION, destination);
        fs.mkdirSync(backupDir, { recursive: true });

        res.data.items
            .filter(group => group.partition != 'Common')
            .forEach(group => {
                const file = path.join(backupDir, `${group.name}.json`);
                console.log(`Processing ${group.name}: ${file}`);
                fs.writeFileSync(file, JSON.stringify(group.records, null, 2));
            });
    } else {
        console.error(`failed to retrieve irules: ${res.status} - ${res.message}`);
    }
}

/**
 * https://clouddocs.f5.com/api/icontrol-rest/APIRef_tm_ltm_rule.html
 */
async function irules(url, destination) {
    const res = await request(`${url}/mgmt/tm/ltm/rule`);

    if (res.status === 200) {
        const backupDir = path.join(BACKUP_LOCATION, destination);
        fs.mkdirSync(backupDir, { recursive: true });

        res.data.items
            .filter(rule => rule.partition != 'Common')
            .forEach(rule => {
                const file = path.join(backupDir, `${rule.name}.tcl`);
                console.log(`Processing ${rule.name}: ${file}`);
                fs.writeFileSync(file, rule.apiAnonymous);
            });
    } else {
        console.error(`failed to retrieve irules: ${res.status} - ${res.message}`);
    }
}

/**
 * Make a request to the F5 applying any common headers such as auth.
 * @param {string} url
 * @returns a promise to the request
 */
async function request(url) {
    return axios.get(url, {
        auth: {
            username: "MoD_Guest",
            password: "ReadOnly"
        }
    });
}

/**
 * https://clouddocs.f5.com/api/icontrol-rest/APIRef_tm_ltm_virtual.html
 */
async function virtualservers(url, destination) {
    const res = await request(`${url}/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules`);

    if (res.status === 200) {
        const backupDir = path.join(BACKUP_LOCATION, destination);
        fs.mkdirSync(backupDir, { recursive: true });

        res.data.items
            .filter(vs => vs.partition != 'Common')
            // only save down the information we want for the virtual servers
            .map(vs => {
                return {
                    name: vs.name,
                    enabled: vs.enabled,
                    pool: vs.pool,
                    profiles: vs.profilesReference.items.map(p => p.name),
                    rules: vs.rules
                }
            })
            .forEach(vs => {
                const file = path.join(backupDir, `${vs.name}.json`);
                console.log(`Processing ${vs.name}: ${file}`);
                fs.writeFileSync(file, JSON.stringify(vs, null, 2));
            });
    } else {
        console.error(`failed to retrieve irules: ${res.status} - ${res.message}`);
    }
}

async function run() {
    await datagroups(F5_NON_PROD, path.join('datagroups', 'non-prod'));
    await datagroups(F5_PROD_PTC, path.join('datagroups', 'prod-ptc'));
    // await datagroups(F5_PROD_CTC, path.join('datagroups', 'prod-ctc'));
    await irules(F5_NON_PROD, path.join('irules', 'non-prod'));
    // await irules(F5_PROD_PTC, path.join('irules', 'prod-ptc'));
    // await irules(F5_PROD_CTC, path.join('irules', 'prod-ctc'));
    // await virtualservers(F5_NON_PROD, path.join('virtualservers', 'non-prod'));
    //await virtualservers(F5_PROD_PTC, path.join('virtualservers', 'prod-ptc'));
    // await virtualservers(F5_PROD_CTC, path.join('virtualservers', 'prod-ctc'));
}

run();
