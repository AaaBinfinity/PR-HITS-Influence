package com.binfinity.chatapp.controller;

import com.binfinity.chatapp.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@CrossOrigin(origins = "*") // 允许所有来源访问
@RestController
@RequestMapping("/friends")
@RequiredArgsConstructor
public class FriendController {
    private static final Logger logger = LoggerFactory.getLogger(FriendController.class);
    private final UserService userService;

    // 添加好友
    @PostMapping("/add")
    public ResponseEntity<?> addFriend(@RequestParam String username, @RequestParam String friendUsername) {
        logger.info("添加好友请求：用户名={}, 好友用户名={}", username, friendUsername);
        try {
            userService.addFriend(username, friendUsername);
            // 记录成功
            logger.info("好友添加成功：用户名={}, 好友用户名={}", username, friendUsername);
            return ResponseEntity.ok("好友添加成功");
        } catch (IllegalArgumentException e) {
            // 记录错误
            logger.error("好友添加失败：用户名={}, 好友用户名={}, 错误信息={}", username, friendUsername, e.getMessage(), e);
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            // 记录服务器错误
            logger.error("服务器错误：用户名={}, 好友用户名={}, 错误信息={}", username, friendUsername, e.getMessage(), e);
            return ResponseEntity.status(500).body("服务器错误");
        }
    }

    // 获取好友列表
    @GetMapping("/list")
    public ResponseEntity<?> getFriends(@RequestParam String username) {
        logger.info("获取好友列表请求：用户名={}", username);
        try {
            List<String> friends = userService.getFriendList(username);
            // 记录成功
            logger.info("好友列表获取成功：用户名={}, 好友数={}", username, friends.size());
            return ResponseEntity.ok(friends);
        } catch (Exception e) {
            // 记录服务器错误
            logger.error("获取好友列表失败：用户名={}, 错误信息={}", username, e.getMessage(), e);
            return ResponseEntity.status(500).body("服务器错误");
        }
    }
}
