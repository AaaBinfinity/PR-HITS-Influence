package com.binfinity.chatapp.controller;

import com.binfinity.chatapp.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@CrossOrigin(origins = "*") // 允许所有来源访问
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {
    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);
    private final UserService userService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> request) {
        logger.info("注册请求：{}", request); // 记录请求内容
        try {
            String username = request.get("username");
            String password = request.get("password");
            userService.register(username, password);
            logger.info("用户 {} 注册成功", username); // 记录成功的注册信息
            return ResponseEntity.ok(Map.of("message", "用户 " + username + " 注册成功"));
        } catch (Exception e) {
            logger.error("注册失败：{}", e.getMessage(), e); // 记录异常信息
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> request) {
        logger.info("登录请求：{}", request); // 记录请求内容
        try {
            String username = request.get("username");
            String password = request.get("password");
            String token = userService.login(username, password);
            logger.info("用户 {} 登录成功，返回 token: {}", username, token); // 记录登录成功和返回的token
            return ResponseEntity.ok(Map.of("username", username, "token", token));
        } catch (Exception e) {
            logger.error("登录失败：{}", e.getMessage(), e); // 记录异常信息
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", e.getMessage()));
        }
    }
}
