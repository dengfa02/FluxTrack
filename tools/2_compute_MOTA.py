import os
import motmetrics as mm

# compute MOTA and IDF1

mota_total = 0.0
idf1_total = 0.0
fp_total = 0.0
fn_total = 0.0
sw_total = 0.0


def compute_mota(gt_file, result_file):
    # 读取文件
    gt = mm.io.loadtxt(gt_file, fmt="mot16", min_confidence=1)  # 读取真值文件，仅保留置信度为1的行
    ts = mm.io.loadtxt(result_file, fmt="mot16")  # 读取跟踪结果文件
    # 创建accumulator并计算MOTA
    acc = mm.utils.compare_to_groundtruth(gt, ts, 'iou', distth=0.5)  # 使用IOU作为距离度量，阈值为0.5
    # 计算指标
    mh = mm.metrics.create()
    summary = mh.compute(acc, metrics=['mota', 'idf1', 'num_false_positives', 'num_misses', 'num_switches'], name='acc')

    mota_value = summary['mota'].iloc[0]  # 获取MOTA值
    idf1_value = summary['idf1'].iloc[0]  # 获取IDF1值
    fp_value = summary['num_false_positives'].iloc[0]
    fn_value = summary['num_misses'].iloc[0]
    sw_value = summary['num_switches'].iloc[0]

    return mota_value, idf1_value, fp_value, fn_value, sw_value


def process_directory(directory1, directory2, output_folder):
    global mota_total, idf1_total, fp_total, fn_total, sw_total
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    # 获取两个目录中的所有文件
    files1 = [f for f in os.listdir(directory1) if f.endswith(".txt")]
    files1.sort()  # 建议排序，保证每次运行顺序一致

    i = 0
    num_seq = len(files1)
    # 遍历每个文件
    for file in files1:
        gt_file = os.path.join(directory1, file)
        result_file = os.path.join(directory2, file)
        if not os.path.exists(result_file):
            continue
        output_file = os.path.join(output_folder, "woODD_mota_output.txt")

        mota_value, idf1_value, fp_value, fn_value, sw_value = compute_mota(gt_file, result_file)
        mota_total += mota_value
        idf1_total += idf1_value  # [修改 5] 累加 IDF1
        fp_total += fp_value
        fn_total += fn_value
        sw_total += sw_value
        # 将MOTA值写入输出文件
        with open(output_file, 'a') as f:
            f.write(f"{file}:\t MOTA: {mota_value:.6f},\t IDF1: {idf1_value:.6f},\t FP: {fp_value}, \t FN:{fn_value},\t SW:{sw_value}" + '\n')

        i += 1
        print(f"[{i}/{num_seq}] \t MOTA: {mota_value:.6f},\t IDF1: {idf1_value:.6f},\t FP: {fp_value}, \t FN:{fn_value},\t SW:{sw_value}")

    mota_total = mota_total / num_seq
    idf1_total = idf1_total / num_seq  # 计算平均 IDF1
    # fp_total = fp_total / num_seq
    # fn_total = fn_total / num_seq
    # sw_total = sw_total / num_seq
    print("All Completed, motal_total", mota_total)
    with open(output_file, 'a') as f:
        f.write('-' * 100 + '\n')
        f.write(f"Total:\t MOTA: {mota_total:.6f},\t IDF1: {idf1_total:.6f},\t FP: {fp_total}, \t FN:{fn_total},\t SW:{sw_total}" + '\n')


if __name__ == '__main__':
    directory1 = r'/data/dcy/MultiUAV/ValLabels'  # GT
    directory2 = r'/home/dcy/small_target_detection/Tracking/MYTracker/tracker/output/predict/fluxTrackTRY'  # predict
    output_folder = r'/home/dcy/small_target_detection/Tracking/MYTracker/tracker/output/mota'  # save

    # directory2 = r'/home/dcy/small_target_detection/Tracking/MultiUAV_Baseline_code_and_submissi/output/predict'  # predict
    # output_folder = r'/home/dcy/small_target_detection/Tracking/MultiUAV_Baseline_code_and_submissi/output/mota'  # save

    process_directory(directory1, directory2, output_folder)
