
'use strict';

const path = require('path');
const { execFile } = require('child_process'); // Use execFile for safer execution
const promisify = require('util.promisify');
const inspect = require('object-inspect');
const colors = require('colors/safe');
const copyFileCB = require('fs-copy-file');

const copyFile = promisify(copyFileCB);
const readFile = promisify(require('fs').readFile);

const getProjectTempDir = require('./getProjectTempDir');

// Sanitize function to prevent injection attacks
function sanitize(input) {
    return input.replace(/[^a-zA-Z0-9-_]/g, '');
}

module.exports = function getLockfile(packageFile, date, {
    npmNeeded,
    only,
    logger = () => {},
} = {}) {
    if (typeof packageFile !== 'string' || packageFile.length === 0) {
        return Promise.reject(colors.red(`\`packageFile\` must be a non-empty string; got ${inspect(packageFile)}`));
    }
    if (typeof date !== 'undefined' && !new Date(date).getTime()) {
        return Promise.reject(colors.red(`\`date\` must be a valid Date format if provided; got ${inspect(date)}`));
    }

    const tmpDirP = getProjectTempDir({ npmNeeded, logger });
    const npmRC = path.join(path.dirname(packageFile), '.npmrc');
    const copyPkg = tmpDirP.then((tmpDir) => {
        logger(colors.blue(`Creating \`package.json\` in temp dir for ${date || '“now”'} lockfile`));
        return Promise.all([
            copyFile(packageFile, path.join(tmpDir, 'package.json')),
            copyFile(npmRC, path.join(tmpDir, '.npmrc')).catch((err) => {
                if (!err || !(/^ENOENT: no such file or directory/).test(err.message)) {
                    throw err;
                }
            }),
        ]);
    });

    // Sanitize the command-line arguments
    const sanitizedDate = sanitize(date || '');
    const sanitizedOnly = sanitize(only || '');

    return Promise.all([tmpDirP, copyPkg]).then(([tmpDir]) => new Promise((resolve, reject) => {
        const PATH = path.join(tmpDir, '../node_modules/.bin');
        logger(colors.blue(`Running npm install to create lockfile for ${date || '“now”'}...`));

        const args = ['install', '--ignore-scripts', '--package-lock', '--package-lock-only'];
        if (sanitizedDate) args.push(`--before=${sanitizedDate}`);
        if (sanitizedOnly) args.push(`--only=${sanitizedOnly}`);

        execFile('npm', args,
            {
                cwd: tmpDir,
                env: {
                    PATH: `${PATH}:${process.env.PATH}`,
                    NODE_ENV: process.env.NODE_ENV,
                },
            },
            (err) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(tmpDir);
                }
            }
        );
    })).then((tmpDir) => {
        logger(colors.blue(`Reading lockfile contents for ${date || '“now”'}...`));
        const lockfile = path.join(tmpDir, 'package-lock.json');
        return readFile(lockfile, { encoding: 'utf-8' });
    });
};
