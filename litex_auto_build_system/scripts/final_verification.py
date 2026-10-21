#!/usr/bin/env python3
"""
最终验证脚本：确认实验可以一键运行和复现
"""

import sys
import os
from pathlib import Path

# 设置环境变量（使用相对路径）
script_dir = Path(__file__).resolve().parent
litex_bin = script_dir.parent.parent / "LitexGeo" / "golitex" / "litex_0.9.116-beta_darwin_arm64" / "litex"
os.environ["LITEX_BIN"] = str(litex_bin)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def check_environment():
    """检查运行环境"""
    print("\n" + "="*60)
    print("1. 环境检查")
    print("="*60)

    # Python版本
    print(f"Python版本: {sys.version.split()[0]}")

    # OpenAI库
    try:
        import openai
        print("✅ openai库已安装")
    except ImportError:
        print("❌ openai库未安装")
        return False

    # Litex编译器
    litex_bin = os.environ.get("LITEX_BIN")
    if litex_bin and Path(litex_bin).exists():
        print(f"✅ Litex编译器: {Path(litex_bin).name}")
    else:
        print("❌ Litex编译器未找到")
        return False

    return True

def check_seed_files():
    """检查种子库文件"""
    print("\n" + "="*60)
    print("2. 种子库检查")
    print("="*60)

    base_dir = Path(__file__).resolve().parent.parent
    seeds = {
        "Definition": base_dir / "database/definition_library_seed.lit",
        "Theorem": base_dir / "database/theorem_library_seed.lit"
    }

    all_exist = True
    for name, path in seeds.items():
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {name:12s}: {path} ({size} 字节)")
        else:
            print(f"❌ {name:12s}: {path} (不存在)")
            all_exist = False

    return all_exist

def check_scripts():
    """检查脚本文件"""
    print("\n" + "="*60)
    print("3. 脚本检查")
    print("="*60)

    base_dir = Path(__file__).resolve().parent
    scripts = {
        "Definition脚本": base_dir / "run_litex_definitions.py",
        "Theorem脚本": base_dir / "run_litex_theorems.py",
        "一键运行脚本": base_dir / "run_all_experiments.sh",
        "验证器": base_dir / "litex_session.py"
    }

    all_exist = True
    for name, path in scripts.items():
        if path.exists():
            print(f"✅ {name:15s}: {path.name}")
        else:
            print(f"❌ {name:15s}: {path} (不存在)")
            all_exist = False

    return all_exist

def test_import():
    """测试导入脚本"""
    print("\n" + "="*60)
    print("4. 导入测试")
    print("="*60)

    # 添加scripts目录到Python路径
    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))

    try:
        from run_litex_definitions import LitexExperimentWithValidation, LITEX_TASKS as def_tasks
        print(f"✅ Definition脚本导入成功 ({len(def_tasks)} 个任务)")
    except Exception as e:
        print(f"❌ Definition脚本导入失败: {e}")
        return False

    try:
        from run_litex_theorems import LitexExperimentWithValidation as TheoremExp, LITEX_TASKS as thm_tasks
        print(f"✅ Theorem脚本导入成功 ({len(thm_tasks)} 个任务)")
    except Exception as e:
        print(f"❌ Theorem脚本导入失败: {e}")
        return False

    return True

def test_validator():
    """测试验证器"""
    print("\n" + "="*60)
    print("5. 验证器测试")
    print("="*60)

    try:
        from litex_session import SessionBackedValidator, find_litex_bin

        litex_bin = find_litex_bin()
        if not litex_bin:
            print("❌ 未找到Litex编译器")
            return False

        print(f"✅ Litex编译器: {Path(litex_bin).name}")

        # 测试Definition验证器
        seed_file = Path("database/definition_library_seed.lit")
        seed = seed_file.read_text(encoding='utf-8')
        validator = SessionBackedValidator(seed, frame_timeout=30.0)

        if validator.session and validator.session.alive:
            print("✅ Session模式初始化成功")
            validator.close()
        else:
            print("❌ Session模式初始化失败")
            return False

    except Exception as e:
        print(f"❌ 验证器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    print("\n" + "="*60)
    print("LitexGeo 实验最终验证")
    print("="*60)

    checks = [
        ("环境", check_environment),
        ("种子库", check_seed_files),
        ("脚本", check_scripts),
        ("导入", test_import),
        ("验证器", test_validator)
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    # 总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:10s}: {status}")
        if not result:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有检查通过！实验可以一键运行。")
        print("="*60)
        print("\n运行方式：")
        print("\n方式1：测试模式（推荐先运行）")
        print("  ./run_all_experiments.sh --test")
        print("  预计耗时: 20-30分钟（每个实验3个任务）")
        print("\n方式2：完整运行")
        print("  ./run_all_experiments.sh")
        print("  预计耗时: 6-10小时（Definition 39个 + Theorem 165个任务）")
        print("\n方式3：单独运行")
        print("  ./run_all_experiments.sh --def-only  # 只运行Definition")
        print("  ./run_all_experiments.sh --thm-only  # 只运行Theorem")
        print("\n详细说明请查看: USAGE_GUIDE.md")
    else:
        print("❌ 有检查项未通过，请先解决上述问题。")
        print("="*60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
