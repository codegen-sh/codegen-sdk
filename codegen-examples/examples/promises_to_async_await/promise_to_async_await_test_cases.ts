// Basic Promise creation and usage examples
export function fetchUserData(userId: number): Promise<any> {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (userId > 0) {
                resolve({
                    id: userId,
                    name: 'User ' + userId,
                    email: `user${userId}@example.com`
                });
            } else {
                reject(new Error('Invalid user ID'));
            }
        }, 1000);
    });
}

function fetchUserPosts(userId: number) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (userId > 0) {
                resolve([
                    { id: 1, title: 'Post 1', userId },
                    { id: 2, title: 'Post 2', userId }
                ]);
            } else {
                reject(new Error('Could not fetch posts'));
            }
        }, 800);
    });
}

function fetchPostComments(postId: number): Promise<any[]> {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (postId > 0) {
                resolve([
                    { id: 1, text: 'Great post!', postId },
                    { id: 2, text: 'Thanks for sharing', postId }
                ]);
            } else {
                reject(new Error('Could not fetch comments'));
            }
        }, 500);
    });
}

// Example of nested .then() calls
async function getUserDataAndPosts(userId: number): Promise<void> {
    fetchUserData(userId)
        .then((user) => {
            console.log('User:', user);
            return fetchUserPosts(user.id);
        })
        .then((posts) => {
            console.log('Posts:', posts);
            return fetchPostComments(posts[0].id);
        })
        .then((comments) => {
            console.log('Comments:', comments);
        })
        .catch((error) => {
            console.error('Error:', error.message);
        });
}



// Promise.all example
function getAllUserInfo(userId: number) {
    return Promise.all([
        fetchUserData(userId),
        fetchUserPosts(userId)
    ])
    .then(([user, posts]) => {
        return {
            user,
            posts
        };
    });
}

// Promise chaining with error handling
function processUserData(userId: number): Promise<void>{
    fetchUserData(userId)
        .then((user) => {
            console.log('Found user:', user);
            return fetchUserPosts(userId); // we are passing in the userID -> getting back the posts
        })
        .then((posts) => { // we have the posts over here and NOW we are going to throw and erro!
            console.log('Found posts:', posts);
            throw new Error('Something went wrong!'); // because an error is going to be thrown!!!

            // this .then will not RESOLVE!!! right???

            // so it's going to reject and go to the cauhgt error.
            // so it's going to go to the cathc block nad handle the erorr
        })
        .then(() => {
            console.log('This will not execute due to the error above');
            return "lol";
        })
        .catch((error) => {
            console.error('Caught error:', error.message);
        })
        .finally(() => {
            console.log('Cleanup operations here');
        });
}



async function processUserDataAsync(userId: number): Promise<void> {
    try {
        const user = await fetchUserData(userId);
        console.log('Found user:', user);

        const posts = await fetchUserPosts(userId);
        console.log('Found posts:', posts);

        throw new Error('Something went wrong!');
        console.log('This will not execute due to the error above');
    } catch (error) {
        console.error('Caught error:', error.message);
    } finally {
        console.log('Cleanup operations here');
    }
}

async function ensureTable(tableName, schemaName, trxOrKnex) {
    const lockTable = getLockTableName(tableName);
    let exists = await getSchemaBuilder(trxOrKnex, schemaName)
      .hasTable(tableName);
        await !exists && _createMigrationTable(tableName, schemaName, trxOrKnex);

        exists = await getSchemaBuilder(trxOrKnex, schemaName).hasTable(lockTable);

        await (
          !exists && _createMigrationLockTable(lockTable, schemaName, trxOrKnex)
        );

        const data = await getTable(trxOrKnex, lockTable, schemaName).select('*');

    return (
          !data.length && _insertLockRowIfNeeded(tableName, schemaName, trxOrKnex)
        );
  }




function create(opts): Promise<any> {
    var qResponse = this.request(opts);
    qResponse = qResponse.then(function success(response) {
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw new Error(response);
      }
      if (typeof response.body === "string") {
        return JSON.parse(response.body);
      }
      return response.body;
    });

    return qResponse;
}

async function createAsync(opts): Promise<any> {
    var qResponse = this.request(opts);
    const response = await qResponse;

    qResponse = (async (response) => {
        if (response.statusCode < 200 || response.statusCode >= 300) {
            throw new Error(response);
          }
          if (typeof response.body === "string") {
            return JSON.parse(response.body);
          }
          return response.body;
    })(response);

    return qResponse;
}

// ======================= Assignment Variable Scenarios  ========================
// Scenario # 1: pass in variable to function
async function functionA(somePromise) {
   const promiseChain = somePromise.then((result) => {
        return processResult(result);
    });
    functionB(promiseChain);
    functionC(promiseChain);
}



function functionAtryCatch(somePromise: Promise<any>) {

    const promiseChain = somePromise.then((result) => {
        return processResult(result);
    }).catch((error) => {
        console.error(error);
        return error;
    }).finally(() => {
        console.log('Cleanup here');
    });

    functionB(promiseChain); // this would accept <Promise<Promise | undefined>>
    functionC(promiseChain);
}


function functionAtryCatchAsync(somePromise: Promise<any>) {
    try {
        result = await somePromise;
        const promiseChain = () => {
            return processResult(result);
        }
    } catch (error) {
        console.error(error);
        const promiseChain = error;
    } finally {
        console.log('Cleanup here');
    }

    functionB(promiseChain);
    functionC(promiseChain);
}


// Determinis




export function test(user_id: number) {
    fetchUserData(user_id).then((user) => {
        console.log(user);
        return "lol";
    })
}

export async function testAsync(user_id: number) {
    const user = await fetchUserData(user_id);
    console.log(user);
    "lol";
}





// Promise.race example
function timeoutPromise(ms: number): Promise<never> {
    return new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Operation timed out')), ms);
    });
}

function fetchWithTimeout(userId: number, timeout: number): Promise<any> {
    return Promise.race([
        fetchUserData(userId),
        timeoutPromise(timeout)
    ]);
}

// Example usage
export function runExamples(): void {
    // Basic nested promises
    getUserDataAndPosts(1);

    // Promise.all
    getAllUserInfo(1)
        .then(info => console.log('All user info:', info))
        .catch(error => console.error('Error getting all info:', error));

    // Promise with error handling
    processUserData(1);

    // Promise with timeout
    fetchWithTimeout(1, 2000)
        .then(result => console.log('Fetched with timeout:', result))
        .catch(error => console.error('Timeout error:', error.message));
}
function getLockTableName(tableName: any) {
    throw new Error("Function not implemented.");
}

function getSchemaBuilder(trxOrKnex: any, schemaName: any) {
    throw new Error("Function not implemented.");
}

function _createMigrationTable(tableName: any, schemaName: any, trxOrKnex: any) {
    throw new Error("Function not implemented.");
}

function _createMigrationLockTable(lockTable: any, schemaName: any, trxOrKnex: any) {
    throw new Error("Function not implemented.");
}

function getTable(trxOrKnex: any, lockTable: any, schemaName: any) {
    throw new Error("Function not implemented.");
}

function _insertLockRowIfNeeded(tableName: any, schemaName: any, trxOrKnex: any) {
    throw new Error("Function not implemented.");
}

function processResult(result: any) {
    throw new Error("Function not implemented.");
}

function functionC(promiseChain: any) {
    throw new Error("Function not implemented.");
}

function functionB(promiseChain: any) {
    throw new Error("Function not implemented.");
}
