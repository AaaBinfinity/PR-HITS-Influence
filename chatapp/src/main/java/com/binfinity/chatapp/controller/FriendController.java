package com.binfinity.chatapp.controller;

import com.binfinity.chatapp.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
@CrossOrigin(origins = "*") // 允许所有来源访问
@RestController
@RequestMapping("/friends")
@RequiredArgsConstructor
public class FriendController {
    private final UserService userService;

    // 添加好友
    @PostMapping("/add")
    public ResponseEntity<?> addFriend(@RequestParam String username, @RequestParam String friendUsername) {
        try {
            userService.addFriend(username, friendUsername);
            return ResponseEntity.ok("好友添加成功");
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("服务器错误");
        }
    }

    // 获取好友列表
    @GetMapping("/list")
    public ResponseEntity<?> getFriends(@RequestParam String username) {
        try {
            List<String> friends = userService.getFriendList(username);
            return ResponseEntity.ok(friends);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("服务器错误");
        }
    }
}
