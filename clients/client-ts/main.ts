/* Copyright © 2022 Nikolay Shishov. All rights reserved.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { io } from "socket.io-client";

const socket = io("http://0.0.0.0:5000");

var serverlog = new Array;

socket.on("connect", () => {
    console.log("[Client] Connection:", socket.connected, "ID:", socket.id);
});

socket.on("disconnect", () => {
    console.log("[Client] Connection:", socket.connected, "ID:", socket.id);
});

socket.on("server_log", (data) => {
    serverlog.push(data)
    console.log("[Server] said:", data);
});

function emitMsg(msg: Object){
    console.log("[Client] send message:", msg);
    return new Promise((resolve) => {
        socket.emit('message', msg, (callback: any) => {
            resolve(callback);
        });
    });
}

emitMsg({"type": "system", "job": "get_server_command_list"})
    .then(answer => console.log("[Client] answer from server: ", answer))
emitMsg({"type": "system", "job": "ssh_connection_init", "params": {"ssh_ip": "server1", "ssh_user": "user", "ssh_pass": "password"}})
    .then(answer => console.log("[Client] answer from server: ", answer))
emitMsg({"type": "module", "job": "ssh", "func": "show_hostname", "params": ""})
    .then(answer => console.log("[Client] answer from server: ", answer))
